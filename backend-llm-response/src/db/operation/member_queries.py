from db.connection.connection import DBMemberConnection
from db.models.schemas import HumanMember, VirtualMember, VirtualMemberProfile
from sqlalchemy.orm import Session


def query_human_members(session: Session, name: str) -> list[HumanMember]:
    try:
        return (
            session.query(HumanMember).filter(HumanMember.member_name == name).first()
        )
    except Exception as e:
        print(f"❌ Error querying human members: {e}")

        session.close()
        print("🔚 Database session closed.")
        raise


def get_virtual_member_prompt(session: Session, bot_name: str) -> str | None:
    """
    仮想メンバーのカスタムプロンプトをDBから取得

    Args:
        session: データベースセッション
        bot_name: Bot名（VirtualMemberのmember_name）

    Returns:
        カスタムプロンプト文字列。見つからない場合はNone
    """
    try:
        # VirtualMemberとVirtualMemberProfileをJOINして取得
        result = (
            session.query(VirtualMemberProfile.custom_prompt)
            .join(
                VirtualMember,
                VirtualMember.member_uuid == VirtualMemberProfile.member_uuid,
            )
            .filter(VirtualMember.member_name == bot_name)
            .first()
        )

        if result and result.custom_prompt:
            return result.custom_prompt

        return None

    except Exception as e:
        print(f"❌ Error querying virtual member prompt for {bot_name}: {e}")
        raise


def main():
    db_member_connection = DBMemberConnection()
    session = db_member_connection.db_member_connection_check()
    human_member = query_human_members(session, "Syota")
    print(human_member)
    session.close()


if __name__ == "__main__":
    main()
