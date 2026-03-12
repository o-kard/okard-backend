# คู่มือสำหรับนักพัฒนา: โมดูลโพสต์ (Post Module)

โมดูลโพสต์เป็นหัวใจสำคัญของแพลตฟอร์ม Okard ช่วยให้ผู้สร้างสามารถเผยแพร่แคมเปญโครงการ, จัดการของรางวัล และโต้ตอบกับชุมชน ตัวโมดูลยังประกอบด้วยการทำนายผลด้วย AI และการจัดการสื่อที่ซับซ้อน

## 1. โครงสร้างโปรแกรม (Program Structure)

โมดูลโพสต์ประกอบด้วยหลายชั้นและทำงานร่วมกับโมดูลอื่นๆ มากมาย (สื่อ, แคมเปญ, รางวัล, โมเดล AI)

### โครงสร้างฝั่ง Backend (`okard-backend/src/modules/post`)
- [controller.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post/controller.py): API สำหรับการค้นหาโพสต์, มุมมองรายละเอียด และการสร้าง/อัปเดตแบบหลายส่วน (Multipart)
- [service.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post/service.py): จัดลำดับการสร้างสิ่งที่ซับซ้อน เช่น โพสต์, แคมเปญย่อย และรางวัล รวมถึงการกระตุ้นการทำนายผลด้วย AI
- [repo.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post/repo.py): จัดการการสืบค้น PostgreSQL ขั้นสูงรวมถึงการค้นหาข้อความแบบเต็ม (Full-text search) และตัวกรองการจัดเรียง
- [model.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post/model.py): กำหนดโมเดล `Post` พร้อมความสัมพันธ์ที่หลากหลาย (สื่อ, แคมเปญ, รางวัล และอื่นๆ)
- [background.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post/background.py): จัดการงานแบบอะซิงโครนัส เช่น การสร้างเวกเตอร์สำหรับการค้นหา

### โครงสร้างฝั่ง Frontend (`okard-frontend/src/modules/post`)
- [api/api.ts](file:///Users/wisapat/Documents/Code/Git/okard-frontend/src/modules/post/api/api.ts): วิธีการใช้คำขอแบบ multipart/form-data (`fetchPosts`, `createPost` และอื่นๆ)
- [PostComponent.tsx](file:///Users/wisapat/Documents/Code/Git/okard-frontend/src/modules/post/PostComponent.tsx): ตัวควบคุมหน้า "สำรวจ" (Explore) ที่จัดการสถานะการค้นหา, ตัวกรอง และการจัดเรียง
- `components/`:
    - `PostForm.tsx`: แบบฟอร์มขนาดใหญ่ที่มีหลายขั้นตอน/ส่วนประกอบสำหรับการสร้างเนื้อหา
    - `SideFilters.tsx`: แถบด้านข้างสำหรับกรองหมวดหมู่และเลือกสถานะ
    - `PostList.tsx`: การแสดงผลแบบตาราง (Grid) สำหรับข้อมูลสรุปของโพสต์

---

## 2. ภาพรวมการทำงาน (Top-Down Functional Overview)

กระบวนการสร้างโพสต์เป็นกระบวนการที่มีการจัดลำดับการทำงานที่ค่อนข้าง "เข้มข้น" (Heavy Orchestration)

```mermaid
sequenceDiagram
    participant User as ผู้ใช้ (Browser)
    participant Front as Frontend (PostForm)
    participant Back as Backend (Post Service)
    participant Svc as บริการที่เกี่ยวข้อง (สื่อ, แคมเปญ, รางวัล, AI)
    participant DB as Postgres DB

    User->>Front: ส่งข้อมูลโพสต์ + แคมเปญ + รางวัล + ไฟล์สื่อ
    Front->>Back: POST /post/with-campaigns (FormData)
    Back->>DB: 1. บันทึกข้อมูลโพสต์พื้นฐาน
    Back->>Svc: 2. บันทึกสื่อ (ไฟล์)
    Back->>Svc: 3. บันทึกแคมเปญ (ข้อมูล + ไฟล์)
    Back->>Svc: 4. บันทึกรางวัล (ข้อมูล + ไฟล์)
    Back->>Svc: 5. กระตุ้นการทำนายผลด้วย AI
    Back-->>Front: ส่งกลับวัตถุโพสต์ที่สร้างแล้ว + ผลการทำนาย
    Front->>User: แสดงหน้าต่างแจ้งผลสำเร็จ / ผลการทำนาย
```

---

## 3. คำอธิบายโปรแกรมย่อย (Subprogram Descriptions)

### Backend: ชั้นคอนโทรลเลอร์ (Controller Layer - [controller.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post/controller.py))

| โปรแกรมย่อย | หน้าที่ความรับผิดชอบ | ข้อมูลเข้า (Input) | ข้อมูลออก (Output) |
| :--- | :--- | :--- | :--- |
| `list_posts` | จัดการการค้นหาโครงการด้วยพารามิเตอร์ที่หลากหลาย | `category`, `q`, `sort`, `state` | `list[PostOut]` |
| `create` | สร้างโพสต์และข้อมูลส่วนประกอบย่อยทั้งหมดอย่างละเอียดจาก FormData | `post_data`, `media`, `campaigns`, `rewards` | `PostOut` |
| `get_post_community` | ดึงสถิติผู้สนับสนุนและการกระจายตัวตามรายเมือง | `post_id` | `PostCommunityOut` |

### Backend: ชั้นบริการ (Service Layer - [service.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post/service.py))

| โปรแกรมย่อย | หน้าที่ความรับผิดชอบ | ข้อมูลเข้า (Input) | ข้อมูลออก (Output) |
| :--- | :--- | :--- | :--- |
| `create_post` | ตัวจัดลำดับหลักสำหรับการสร้างวัตถุข้ามโมดูล | `db`, `clerk_id`, `post_data`, `files...` | วัตถุ `Post` |
| `update_post` | จัดการการเปรียบเทียบข้อมูลและการแก้ไข (Patching) แคมเปญและรางวัลที่ซับซ้อน | `db`, `post_id`, `post_data`, `payloads...` | วัตถุ `Post` |
| `update_prediction` | เตรียมคุณลักษณะของโพสต์และเรียกใช้บริการทำนายผลด้วย AI | `db`, `post_id` | ไม่มี (อัปเดตลงฐานข้อมูล) |

### Frontend: ส่วนประกอบต่างๆ (Components - [components/](file:///Users/wisapat/Documents/Code/Git/okard-frontend/src/modules/post/components))

| โปรแกรมย่อย | หน้าที่ความรับผิดชอบ | ข้อมูลเข้า (Input) | ข้อมูลออก (Output) |
| :--- | :--- | :--- | :--- |
| `PostComponent` | ตัวจัดการสถานะการสำรวจทั่วโลก (ซิงค์ข้อมูลกับ URL) | `searchParams` | UI สำหรับการสำรวจ |
| `PostForm` | การจัดการสถานะแบบฟอร์มสำหรับชุดข้อมูลที่ซ้อนกันและซับซ้อน | `initialData` (ทางเลือก) | การส่งข้อมูลแบบ `FormData` |

---

## 4. การสื่อสารและพารามิเตอร์ (Communication & Parameters)

1.  **FormData ที่ถูกจัดลำดับ**: การสร้าง/อัปเดตใช้พารามิเตอร์ `FormData` เพียงอันเดียวซึ่งประกอบด้วย:
    - `data`: ข้อความ JSON ของหัวข้อ/คำอธิบายโพสต์
    - `campaigns`/`rewards`: ข้อความ JSON ของรายการวัตถุที่ซ้อนอยู่ข้างใน
    - `media`/`campaign_media`/`reward_media`: รายการไฟล์ที่ตรงกับดัชนี JSON แบบ 1:1
2.  **การจัดการสถานะ**: โพสต์จะเปลี่ยนสถานะตามลำดับ: `draft` -> `published` -> `success` / `failed` / `archived`
3.  **การพึ่งพาข้ามโมดูล**: โมดูลโพสต์เรียกใช้ `CampaignService`, `RewardService`, `MediaService` และ `ModelService` โดยตรงภายในบล็อกการทำธุรกรรม (Transaction block) ในไฟล์ `service.py`
4.  **การทำงานร่วมกับ AI**: เมื่อมีการสร้างหรือแก้ไข ข้อความและข้อมูล Meta ของโพสต์จะถูกส่งไปยังโมเดลการทำนายเพื่อประเมินความเสี่ยงและโอกาสในการบรรลุเป้าหมาย
