from .celery_app import celery_app

@celery_app.task
def send_ticket_notification(user_id: int, session_id: int, place_number: int):
    print(
        f"User {user_id} bought ticket for session {session_id}, place {place_number}"
    )