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
    archived = "archived"

class PostStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class PostCategory(str, enum.Enum):
    tech = "tech"
    education = "education"
    health = "health"
    other = "other"

class ReportType(str, enum.Enum):
    edit = "edit"
    problem = "problem"

class ReferenceType(str, enum.Enum):
    post = "post"
    campaign = "campaign"
    user = "user"
    progress = "progress"
    reward = "reward"


# oweifiojwefiojqfw
# ifiqfqf