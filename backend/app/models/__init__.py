# Import every model so Base.metadata knows about all tables.
from app.models.appointment import Appointment, AppointmentStatus  # noqa: F401
from app.models.doctor import Doctor, DoctorSchedule  # noqa: F401
from app.models.user import Role, User  # noqa: F401
