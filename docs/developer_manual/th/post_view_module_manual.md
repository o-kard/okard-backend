# คู่มือสำหรับนักพัฒนา: โมดูลการเข้าชมโพสต์ (Post View Module)

โมดูลการเข้าชมโพสต์เป็นบริการยูทิลิตี้ที่ติดตามประวัติปฏิสัมพันธ์ของผู้ใช้ โดยมีวัตถุประสงค์หลักเพื่อส่งข้อมูลให้กับอัลกอริทึมการแนะนำ

## 1. โครงสร้างโปรแกรม (Program Structure)

โมดูลการเข้าชมโพสต์เป็นบริการที่เรียบง่ายแต่มีความสำคัญสูง เนื่องจากมีการเขียนข้อมูล (Write) ถี่มาก

### โครงสร้างฝั่ง Backend (`okard-backend/src/modules/post_view`)
- [service.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post_view/service.py): จัดการตรรกะในการบันทึกการเข้าชม
- [repo.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post_view/repo.py): ใช้ตรรกะแบบ `upsert` เพื่ออัปเดตเวลาการเข้าชมล่าสุด
- [model.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post_view/model.py): กำหนดตาราง `post_view` พร้อมฟิลด์ `user_id`, `post_id` และ `view_count`

---

## 2. ภาพรวมการทำงาน (Top-Down Functional Overview)

การเข้าชมจะถูกบันทึกอย่างเงียบๆ ในขั้นตอนเบื้องหลังเมื่อมีการเรียกดูข้อมูลโพสต์

```mermaid
graph LR
    API[Post Controller] -->|กระตุ้น| ViewSvc[Post View Service]
    ViewSvc -->|Upsert| DB[(ตาราง post_view)]
    DB -->|อ่านข้อมูล| ForYou[โมดูล สำหรับคุณ]
```

---

## 3. คำอธิบายโปรแกรมย่อย (Subprogram Descriptions)

### Backend: ชั้นบริการ (Service Layer - [service.py](file:///Users/wisapat/Documents/Code/Git/okard-backend/src/modules/post_view/service.py))

| โปรแกรมย่อย | หน้าที่ความรับผิดชอบ | ข้อมูลเข้า (Input) | ข้อมูลออก (Output) |
| :--- | :--- | :--- | :--- |
| `log_post_view` | เพิ่มจำนวนการเข้าชมหรือสร้างบันทึกใหม่สำหรับคู่ผู้ใช้/โพสต์ | `db`, `user_id`, `post_id` | ไม่มี |

---

## 4. การสื่อสารและพารามิเตอร์ (Communication & Parameters)

1.  **การกระตุ้นแบบเงียบ**: `PostController` จะกระตุ้นการทำงานของ `log_post_view` โดยอัตโนมัติทุกครั้งที่มีการเรียกดูรายละเอียดโพสต์พร้อมกับ `clerk_id` ที่ผ่านการตรวจสอบสิทธิ์แล้ว
2.  **ตรรกะการอัปเดต (Upsert Logic)**: เพื่อจัดการการเข้าชมซ้ำอย่างมีประสิทธิภาพ ชั้น Repository จะใช้รูปแบบ "Upsert on Conflict" โดยจะอัปเดตเวลา `updated_at` แทนการสร้างแถวข้อมูลใหม่ที่ซ้ำซ้อน
3.  **การใช้งานปลายทาง**: ข้อมูลนี้เป็นอินพุตหลักสำหรับการคำนวณเวกเตอร์ความชอบ (Preference vector) ในโมดูล `for_you`
4.  **ขนาดข้อมูล**: ตารางนี้ได้รับการออกแบบมาเพื่อการอัปเดตที่มีความถี่สูง และควรมีการสร้างดัชนี (Index) ในฟิลด์ `(user_id, post_id)`
