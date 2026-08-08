import httpx


class FileTypeError(Exception):
    def __init__(self, filetype: str):
        self.filetype = filetype
        super().__init__(f"File type must be PDF. You have uploaded: {self.filetype}")


class TelegramAPIError(Exception):
    def __init__(self, error_code: int, description: str):
        self.error_code = error_code
        self.description = description
        super().__init__(f"Telegram API error {error_code}: {description}")

class PDFAlreadyExists(Exception):
     def __init__(self,pid: int, name: str):
        self.name = name
        self.pid = pid
        super().__init__(f"{self.name}.pdf already exists")

class PDFNotFound(Exception):
     def __init__(self,pid: int):
        self.pid = pid
        super().__init__(f"PDF id: {self.pid} not found")

class PDFLoadError(Exception):
     def __init__(self,pid: int):
        self.pid = pid
        super().__init__(f"PDF id: {self.pid} not found at storage address")

class UploadPDFBeforeQuery(Exception):
     def __init__(self):
        super().__init__(f"Upload a PDF first")

class NoExtractableTextFound(Exception):
         def __init__(self,pid: int):
            self.pid = pid
            super().__init__(f"No extractable text found in pdf")


class UserNotExist(Exception):
    def __init__(self, userid: int):
            self.userid = userid
            super().__init__(f"User does not exist.")
