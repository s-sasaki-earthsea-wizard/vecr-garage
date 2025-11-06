from db.connection.connection import DBMemberConnection
from db.models.schemas import HumanMember, VirtualMember


class MemberService:
    def __init__(self):
        self.db_connection = DBMemberConnection()

    def get_member_responses(self) -> dict:
        session = self.db_connection.db_member_connection_check()

        try:
            # 仮実装として、member_idをハードコード
            human_member = session.query(HumanMember).filter(HumanMember.member_id == 1).first()
            virtual_member = (
                session.query(VirtualMember).filter(VirtualMember.member_id == 1).first()
            )

            if not human_member or not virtual_member:
                raise ValueError("Members not found")

            return {
                "human_response": f"わたしの名前は{human_member.member_name}です",
                "virtual_response": f"あなたの名前は{virtual_member.member_name}です",
            }

        finally:
            session.close()


def main():
    service = MemberService()
    try:
        responses = service.get_member_responses()
        print("\n=== メンバーレスポンス ===")
        print(f"人間メンバー: {responses['human_response']}")
        print(f"仮想メンバー: {responses['virtual_response']}")
        print("=======================\n")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")


if __name__ == "__main__":
    main()
