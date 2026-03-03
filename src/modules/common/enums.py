import enum

class NotificationType(str, enum.Enum):
    comment = "comment"
    like = "like"
    system_alert = "system_alert"
    reminder = "reminder"
    goal = "goal"

class PaymentMethod(str, enum.Enum):
    promptpay = "promptpay"
    card = "card"
    true_money_wallet = "true_money_wallet"
    pay_by_bank = "pay_by_bank"

class PostState(str, enum.Enum):
    draft = "draft"
    published = "published"
    fail = "fail"
    success = "success"
    suspend = "suspend"

class PostCategory(str, enum.Enum):
    art = "art"
    comics = "comics"
    crafts = "crafts"
    dance = "dance"
    design = "design"
    fashion = "fashion"
    filmVideo = "filmVideo"
    food = "food"
    games = "games"
    journalism = "journalism"
    music = "music"
    photography = "photography"
    publishing = "publishing"
    technology = "technology"
    theater = "theater"
    tech = "tech"
    education = "education"
    health = "health"
    other = "other"

class ReportType(str, enum.Enum):
    problem = "problem"
    spam = "spam"
    inappropriate = "inappropriate"

class ReportStatus(str, enum.Enum):
    pending = "pending"
    investigating = "investigating"
    resolved = "resolved"
    dismissed = "dismissed"

class ReferenceType(str, enum.Enum):
    post = "post"
    campaign = "campaign"
    user = "user"
    progress = "progress"
    reward = "reward"
    report = "report"

class EditRequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"
    cancelled = "cancelled"

class VoteDecision(str, enum.Enum):
    approve = "approve"
    reject = "reject"

class VerificationStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"

class UserRole(str, enum.Enum):
    user = "user"
    creator = "creator"
    admin = "admin"

class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    banned = "banned"

class StorageProvider(str, enum.Enum):
    local = "local"
    s3 = "s3"
    gcs = "gcs"

class VerificationDocType(str, enum.Enum):
    id_card = "id_card"
    house_registration = "house_registration"
    bank_statement = "bank_statement"