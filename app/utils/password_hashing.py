import base64
import hashlib
import os
import struct

def parse_aspnet_identity_hash(pw_hash: str) -> dict:
    data = base64.b64decode(pw_hash)
    if not data:
        raise ValueError("empty password hash")

    format_marker = data[0]
    if format_marker == 0x00:
        salt = data[1:17]
        subkey = data[17:]
        return {
            "version": 2,
            "prf": 0,
            "iter": 1000,
            "salt_len": len(salt),
            "subkey_len": len(subkey),
            "salt": salt,
            "subkey": subkey,
        }
    if format_marker == 0x01:
        prf_le = struct.unpack("<I", data[1:5])[0]
        prf_be = struct.unpack(">I", data[1:5])[0]
        iter_le = struct.unpack("<I", data[5:9])[0]
        iter_be = struct.unpack(">I", data[5:9])[0]
        salt_len_le = struct.unpack("<I", data[9:13])[0]
        salt_len_be = struct.unpack(">I", data[9:13])[0]

        if prf_le in (0, 1, 2) and salt_len_le <= 1024:
            prf = prf_le
            iter_count = iter_le
            salt_len = salt_len_le
            endian = "<"
        elif prf_be in (0, 1, 2) and salt_len_be <= 1024:
            prf = prf_be
            iter_count = iter_be
            salt_len = salt_len_be
            endian = ">"
        else:
            prf = prf_le
            iter_count = iter_le
            salt_len = salt_len_le
            endian = "<"

        salt = data[13 : 13 + salt_len]
        subkey = data[13 + salt_len :]
        return {
            "version": 3,
            "prf": prf,
            "iter": iter_count,
            "salt_len": salt_len,
            "subkey_len": len(subkey),
            "endian": endian,
            "salt": salt,
            "subkey": subkey,
        }
    raise ValueError(f"unsupported password hash format: {format_marker}")


def hash_password_aspnet_identity(password: str, template_hash: str) -> str:
    info = parse_aspnet_identity_hash(template_hash)
    salt = os.urandom(info["salt_len"])

    prf_map = {0: "sha1", 1: "sha256", 2: "sha512"}
    if info["prf"] not in prf_map:
        raise ValueError(f"unsupported PRF: {info['prf']}")

    subkey = hashlib.pbkdf2_hmac(
        prf_map[info["prf"]],
        password.encode("utf-8"),
        salt,
        info["iter"],
        info["subkey_len"],
    )

    if info["version"] == 2:
        data = b"\x00" + salt + subkey
    else:
        endian = info.get("endian", "<")
        data = (
            b"\x01"
            + struct.pack(f"{endian}I", info["prf"])
            + struct.pack(f"{endian}I", info["iter"])
            + struct.pack(f"{endian}I", info["salt_len"])
            + salt
            + subkey
        )

    return base64.b64encode(data).decode("utf-8")


def verify_password_aspnet_identity(password: str, pw_hash: str) -> bool:
    info = parse_aspnet_identity_hash(pw_hash)
    prf_map = {0: "sha1", 1: "sha256", 2: "sha512"}
    if info["prf"] not in prf_map:
        return False
    subkey = hashlib.pbkdf2_hmac(
        prf_map[info["prf"]],
        password.encode("utf-8"),
        info["salt"],
        info["iter"],
        info["subkey_len"],
    )
    return subkey == info["subkey"]
