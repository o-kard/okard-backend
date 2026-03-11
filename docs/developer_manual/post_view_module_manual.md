# Developer Manual: Post View Module

The Post View module is a utility service that tracks user interaction history, primarily to fuel the recommendation algorithm.

## 1. Program Structure

The Post View module is a simple but critical high-write service.

### Backend Structure (`okard-backend/src/modules/post_view`)
- [service.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post_view/service.py): Handles the logic for logging a view.
- [repo.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post_view/repo.py): Uses `upsert` logic to update the last view timestamp.
- [model.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post_view/model.py): Defines the `post_view` table with `user_id`, `post_id`, and `view_count`.

---

## 2. Top-Down Functional Overview

Views are logged silently in the background when a post is retrieved.

```mermaid
graph LR
    API[Post Controller] -->|Trigger| ViewSvc[Post View Service]
    ViewSvc -->|Upsert| DB[(post_view Table)]
    DB -->|Read| ForYou[For You Module]
```

---

## 3. Subprogram Descriptions

### Backend: Service Layer ([service.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post_view/service.py))

| Subprogram | Responsibility | Input | Output |
| :--- | :--- | :--- | :--- |
| `log_post_view` | Increments view count or creates a new record for a user/post pair. | `db`, `user_id`, `post_id` | N/A |

---

## 4. Communication & Parameters

1.  **Silent Trigger**: The `PostController` triggers `log_post_view` automatically whenever a detailed post view is requested with an authenticated `clerk_id`.
2.  **Upsert Logic**: To handle repetitive views efficiently, the repository uses an "Upsert on Conflict" pattern, updating the `updated_at` timestamp rather than creating duplicate rows.
3.  **Downstream Consumption**: This data is the primary input for the `for_you` module's preference vector calculation.
4.  **Scale**: This table is designed for high-frequency updates and should be indexed on `(user_id, post_id)`.
