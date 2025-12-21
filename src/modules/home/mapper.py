# # src/modules/post/mapper.py
# from src.modules.home.schema import HomePostOut

# def map_post_to_home(p) -> HomePostOut:
#     base = HomePostOut.model_validate(
#         p,
#         from_attributes=True,
#         context={"progress": True},  
#     )

#     return base.model_copy(
#         update={
#             "progress": int((p.current_amount / p.goal_amount) * 100)
#             if p.goal_amount else 0
#         }
#     )
