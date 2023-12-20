class User:

    def __init__(self, username : str, password : str) -> None:
        self.username = username
        self.password = password
    
    def get_user(self) -> str:
        return self.username
    
    def get_password(self) -> str:
        return self.password

    @staticmethod
    def is_authenticated() -> bool:
        return True
    
    @staticmethod
    def is_active() -> bool:
        return True
    
    @staticmethod
    def is_anonymous() -> bool:
        return False

    def get_id(self) -> str:
        return self.username

