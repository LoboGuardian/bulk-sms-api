# import bcrypt
# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# class Authenticate:
#     def create_salt_and_hashed_password(self, *, plaintext_password: str) :
#         salt = self.generate_salt()
#         hashed_password = self.hash_password(
#             password=plaintext_password, salt=salt)
#         return hashed_password

#     @staticmethod
#     def generate_salt() -> str:
#         return bcrypt.gensalt().decode()

#     @staticmethod
#     def hash_password(*, password: str, salt: str) -> str:
#         return pwd_context.hash(password + salt)
