import sqlite3
from fastmcp import FastMCP

from app.config import AKIRA_DB_PATH
from app.utils.password_hashing import (
    hash_password_aspnet_identity,
    verify_password_aspnet_identity,
)


def register(mcp: FastMCP) -> None:
    @mcp.tool
    def check_akira_db_user(username: str) -> dict:
        """Check whether a user exists in the Akira DB."""
        conn = sqlite3.connect(AKIRA_DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                "select Id, UserName, NormalizedUserName, Email from AspNetUsers where UserName = ?",
                (username,),
            )
            row = cur.fetchone()
            if not row:
                return {"exists": False, "user": None}
            return {
                "exists": True,
                "user": {
                    "id": row[0],
                    "username": row[1],
                    "normalized_username": row[2],
                    "email": row[3],
                },
            }
        finally:
            conn.close()

    @mcp.tool
    def get_akira_user_state(username: str) -> dict:
        """Get auth-related flags for a user in Akira DB."""
        conn = sqlite3.connect(AKIRA_DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                select
                    UserName, NormalizedUserName, EmailConfirmed, PhoneNumberConfirmed,
                    TwoFactorEnabled, LockoutEnabled, LockoutEnd, AccessFailedCount
                from AspNetUsers where UserName = ?
                """,
                (username,),
            )
            row = cur.fetchone()
            if not row:
                return {"exists": False}
            return {
                "exists": True,
                "username": row[0],
                "normalized_username": row[1],
                "email_confirmed": bool(row[2]),
                "phone_confirmed": bool(row[3]),
                "two_factor_enabled": bool(row[4]),
                "lockout_enabled": bool(row[5]),
                "lockout_end": row[6],
                "access_failed_count": row[7],
            }
        finally:
            conn.close()

    @mcp.tool
    def reset_akira_password(username: str, new_password: str) -> dict:
        """Reset a user's password in the Akira DB using ASP.NET Identity hashing."""
        conn = sqlite3.connect(AKIRA_DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                "select PasswordHash from AspNetUsers where UserName = ?",
                (username,),
            )
            row = cur.fetchone()
            if not row or not row[0]:
                return {"updated": False, "reason": "user_not_found_or_no_hash"}

            new_hash = hash_password_aspnet_identity(new_password, row[0])
            cur.execute(
                "update AspNetUsers set PasswordHash = ? where UserName = ?",
                (new_hash, username),
            )
            conn.commit()
            return {"updated": cur.rowcount == 1}
        finally:
            conn.close()

    @mcp.tool
    def verify_akira_password(username: str, password: str) -> dict:
        """Verify a password against the stored hash in Akira DB."""
        conn = sqlite3.connect(AKIRA_DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                "select PasswordHash from AspNetUsers where UserName = ?",
                (username,),
            )
            row = cur.fetchone()
            if not row or not row[0]:
                return {"verified": False, "reason": "user_not_found_or_no_hash"}
            verified = verify_password_aspnet_identity(password, row[0])
            return {"verified": verified}
        finally:
            conn.close()

    @mcp.tool
    def unlock_akira_user(username: str) -> dict:
        """Reset lockout and confirmation flags to allow login."""
        conn = sqlite3.connect(AKIRA_DB_PATH)
        try:
            cur = conn.cursor()
            cur.execute(
                """
                update AspNetUsers
                set
                    AccessFailedCount = 0,
                    LockoutEnabled = 0,
                    LockoutEnd = NULL,
                    TwoFactorEnabled = 0,
                    EmailConfirmed = 1,
                    PhoneNumberConfirmed = 1
                where UserName = ?
                """,
                (username,),
            )
            conn.commit()
            return {"updated": cur.rowcount == 1}
        finally:
            conn.close()
