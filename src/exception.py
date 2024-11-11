import sys  #to access all inbuilt errors

def error_message_detail(error,error_detail:sys):   #error detail is coming from sys class
    _,_,exc_tb=error_detail.exc_info()      #there are total three outputs are generated through exc_info() but the third argument consists of filename including line no

    file_name=exc_tb.tb_frame.f_code.co_filename    #proper filename

    error_message="Error occurred python script name [{0}] line number [{1}] error_message[{2}]".format(
        file_name,exc_tb.tb_lineno,str(error)       
    )   #Custom error message

    return error_message       #finally after completely formatting it finally return the modified message


class CustomException(Exception):
    def __init__(self,error_message,error_detail):
        super().__init__(error_message)
        self.error_message=error_message_detail(error=error_message,error_detail=error_detail)
    
    def __str__(self):
        return self.error_message