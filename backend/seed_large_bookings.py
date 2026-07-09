import sys
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

# Add current directory to python path to resolve app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, delete
from app.core.database import SessionLocal
from app.modules.auth.models import User
from app.modules.booking.models import Booking
from app.modules.profile.models import UserProfile

KOL_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
CUSTOMER_DEMO_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")

MOCK_GUESTS = [
    ("Khánh Trần", "0912345678"),
    ("Bình Nguyễn", "0987654321"),
    ("Hải Đỗ", "0905556667"),
    ("Thanh Lê", "0977888999"),
    ("Duy Phạm", "0933444555"),
    ("Quỳnh Phan", "0966777888"),
    ("Nam Vũ", "0944111222"),
    ("Tú Hoàng", "0922333444"),
    ("Linh Đặng", "0988999000"),
    ("Sơn Ngô", "0955666777"),
    ("Hương Trịnh", "0977222333"),
    ("Minh Đào", "0911000222"),
]

NOTES_POOL = [
    "Duo ranked tối nay",
    "Coach aim 2 giờ hôm nay",
    "Giao lưu custom room",
    "Squad 4 trận cuối tuần",
    "Collab làm content Tiktok",
    "Review VOD đấu giải",
    "Marathon leo rank cuối tuần",
    "Training kỹ năng macro",
    "Trận đấu showmatch",
    "Duo rank Bạch Kim/Kim Cương",
]

def _build_vietqr_url(bank_code: str, bank_account: str, bank_name: str, amount: int, code: str, guest: str) -> str:
    add_info = quote(f"{code} {guest}".strip(), safe="")
    name_q = quote(bank_name, safe="")
    return (
        f"https://img.vietqr.io/image/{bank_code}-{bank_account}-compact2.png"
        f"?amount={amount}&addInfo={add_info}&accountName={name_q}"
    )

def main():
    print("Starting database seeding with large volume booking data...")
    db = SessionLocal()
    try:
        # Check KOL user exists
        kol = db.get(User, KOL_ID)
        if not kol:
            print(f"Error: KOL with ID {KOL_ID} does not exist in the database.")
            return

        kol_profile = db.scalar(select(UserProfile).where(UserProfile.user_id == KOL_ID))
        if not kol_profile:
            print(f"Error: KOL UserProfile for {KOL_ID} does not exist.")
            return

        # Ensure creator has pricing & bank details set
        kol_profile.pricing_type = "match"
        kol_profile.price_per_match = 150000
        kol_profile.price_per_hour = 100000
        kol_profile.currency = "VND"
        kol_profile.bank_name = kol_profile.bank_name or "MB Bank"
        kol_profile.bank_code = kol_profile.bank_code or "970422"
        kol_profile.bank_account_number = kol_profile.bank_account_number or "0962954690"
        kol_profile.bank_account_name = kol_profile.bank_account_name or "CREATOR DEMO"
        db.add(kol_profile)
        db.flush()

        bank_code = kol_profile.bank_code
        bank_account = kol_profile.bank_account_number
        bank_name = kol_profile.bank_account_name

        # Query all customer users
        customers = db.scalars(select(User).where(User.role == "customer")).all()
        customer_ids = [c.id for c in customers]
        if CUSTOMER_DEMO_ID not in customer_ids:
            # Fallback to customer list or CUSTOMER_DEMO_ID
            customer_ids.append(CUSTOMER_DEMO_ID)

        # Clear existing bookings for this KOL to avoid primary key issues & clean slate
        print(f"Clearing old bookings for KOL {KOL_ID}...")
        db.execute(delete(Booking).where(Booking.kol_user_id == KOL_ID))
        db.commit()

        # Date parameters
        now = datetime.now(timezone.utc)
        # Seed years: 2024, 2025, 2026
        # Generate monthly batches
        total_seeded = 0
        
        for year in [2024, 2025, 2026]:
            for month in range(1, 13):
                # Calculate if month is in past, present, or future
                month_date = datetime(year, month, 15, tzinfo=timezone.utc)
                is_past = month_date < now.replace(day=15)
                is_present = (year == now.year and month == now.month)
                
                # Determine booking count per month (simulate seasonal growth)
                if year == 2024:
                    num_bookings = random.randint(6, 12)
                elif year == 2025:
                    num_bookings = random.randint(10, 18)
                else: # 2026
                    num_bookings = random.randint(12, 22)

                print(f"Generating {num_bookings} bookings for {month:02d}/{year}...")
                
                for idx in range(num_bookings):
                    # Random day in month
                    day = random.randint(1, 28)
                    hour = random.randint(8, 22)
                    minute = random.randint(0, 59)
                    scheduled_at = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

                    # Determine pricing and calculations
                    pricing_type = random.choice(["match", "hourly"])
                    quantity = random.randint(1, 4)
                    unit_price = 150000 if pricing_type == "match" else 100000
                    total_amount = unit_price * quantity

                    # Determine status distributions
                    if is_past:
                        # Mostly completed, some cancelled or confirmed
                        rand = random.random()
                        if rand < 0.75:
                            status = "completed"
                            payment_status = "paid"
                        elif rand < 0.90:
                            status = "cancelled"
                            payment_status = "unpaid"
                        else:
                            status = "confirmed"
                            payment_status = random.choice(["paid", "unpaid"])
                    elif is_present:
                        # Mix of all statuses
                        rand = random.random()
                        if rand < 0.40:
                            status = "completed"
                            payment_status = "paid"
                        elif rand < 0.70:
                            status = "confirmed"
                            payment_status = random.choice(["paid", "unpaid"])
                        elif rand < 0.85:
                            status = "pending"
                            payment_status = "unpaid"
                        else:
                            status = "cancelled"
                            payment_status = "unpaid"
                    else:
                        # Future bookings: pending or confirmed
                        rand = random.random()
                        if rand < 0.60:
                            status = "pending"
                            payment_status = "unpaid"
                        elif rand < 0.90:
                            status = "confirmed"
                            payment_status = "unpaid"
                        else:
                            status = "confirmed"
                            payment_status = "paid"

                    # Select guest/customer
                    if random.random() < 0.3:
                        # Guest booking (no login)
                        guest_name, guest_phone = random.choice(MOCK_GUESTS)
                        customer_user_id = None
                    else:
                        # Registered customer booking
                        customer_user_id = random.choice(customer_ids)
                        guest_name = "Customer Demo" if customer_user_id == CUSTOMER_DEMO_ID else f"Khách Hàng {str(customer_user_id)[:4]}"
                        guest_phone = f"0901{random.randint(100000, 999999)}"

                    # Generate payment code
                    short_uuid = str(uuid.uuid4()).replace("-", "")[:6].upper()
                    payment_code = f"BK{year % 100}{month:02d}{short_uuid}"
                    
                    # Generate payment QR
                    payment_qr_url = _build_vietqr_url(
                        bank_code, bank_account, bank_name, total_amount, payment_code, guest_name
                    )

                    # Instantiate booking
                    booking = Booking(
                        id=uuid.uuid4(),
                        kol_user_id=KOL_ID,
                        customer_user_id=customer_user_id,
                        guest_name=guest_name,
                        guest_phone=guest_phone,
                        scheduled_at=scheduled_at,
                        pricing_type=pricing_type,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_amount=total_amount,
                        currency="VND",
                        payment_qr_url=payment_qr_url,
                        payment_code=payment_code,
                        payment_status=payment_status,
                        status=status,
                        notes=random.choice(NOTES_POOL),
                        source="system",
                        progress_percent=100 if status == "completed" else 0
                    )
                    
                    # Set payment proof fields if paid
                    if payment_status == "paid":
                        booking.payment_proof_url = "https://example.com/proofs/demo.png"
                        booking.payment_proof_note = "Đã thanh toán chuyển khoản thành công"
                        booking.payment_proof_uploaded_at = scheduled_at - timedelta(minutes=random.randint(5, 30))
                        booking.payment_reviewed_at = scheduled_at + timedelta(minutes=random.randint(1, 10))

                    db.add(booking)
                    total_seeded += 1

        db.commit()
        print(f"Successfully seeded {total_seeded} bookings spanning Jan 2024 to Dec 2026!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
