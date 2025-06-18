from sqlalchemy.orm import Session

from db.models.schemas import HumanMember
from db.connection.connection import DBMemberConnection

def query_human_members(session: Session, name: str) -> list[HumanMember]:
    try:
        return session.query(HumanMember).filter(HumanMember.member_name == name).first()
    except Exception as e:
        print(f"❌ Error querying human members: {e}")
        
        session.close()
        print(f"🔚 Database session closed.")
        raise

def main():
    db_member_connection = DBMemberConnection()
    session = db_member_connection.db_member_connection_check()
    human_member = query_human_members(session, "Syota")
    print(human_member)
    session.close()

if __name__ == "__main__":
    main()