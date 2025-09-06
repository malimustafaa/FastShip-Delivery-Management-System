


from fastapi import FastAPI, HTTPException, Request,status
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse



class FastShipException(Exception):
    status = status.HTTP_400_BAD_REQUEST
    """ Base Exception for all exceptions in fastship api."""

class EntityNotFound(FastShipException):
    """Entity not found. """
    status = status.HTTP_404_NOT_FOUND

class ClientNotAuthorized(FastShipException):
    """Client is not authorized to perform the action"""
    status = status.HTTP_401_UNAUTHORIZED

class BadCredentials(FastShipException):
    "User Email or Password is incorrect"
    status = status.HTTP_401_UNAUTHORIZED

class InvalidToken(FastShipException):
    """Access token is invalid or expired"""
    status = status.HTTP_401_UNAUTHORIZED

class DeliveryPartnerNotAvailable(FastShipException):
    """Delivery Partner isnt available"""
    status= status.HTTP_404_NOT_FOUND

class VerificationCodeRequired(FastShipException):
    """Verification code required"""
    status= status.HTTP_400_BAD_REQUEST

class NoTokenData(FastShipException):
    "No token data Found."""
    status = status.HTTP_401_UNAUTHORIZED

class TagDoesNotExist(FastShipException):
    """Tag Does not exist in shipment. """

class TokenDataExpired(FastShipException):
    """Token Data expired! """
    status = status.HTTP_401_UNAUTHORIZED

class SellerNotFound(FastShipException):
    """Seller Not found."""
    status = status.HTTP_404_NOT_FOUND

class PartnerNotFound(FastShipException):
    """Delivery Partner not found."""
    status = status.HTTP_404_NOT_FOUND

class InvalidInput(FastShipException):
    """ Invalid Input."""
    status = status.HTTP_400_BAD_REQUEST

class IncorrectPassword(FastShipException):
    """ Incorrect Password! """
    status = status.HTTP_401_UNAUTHORIZED

class EmailNotVerified(FastShipException):
    """ Email Not Verified! """
    status = status.HTTP_401_UNAUTHORIZED

class NoRelevantPartnerFound(FastShipException):
    """ No Partner found in this zipcode area"""
    status = status.HTTP_401_UNAUTHORIZED

def _get_handler(status:int,detail:str):
    def handler(request:Request,exception:Exception): #passed by fastapi internally when exception raised, we dont have to pass these arguments
     from rich import print,panel
     print(panel.Panel(f"Handled: {exception.__class__.__name__}"))
     raise HTTPException(status_code=status,detail=detail)
    return handler
    



#exception handlers

def add_exception_handlers(app:FastAPI):
    #creates app handler for all subclasses
    for subclass in FastShipException.__subclasses__():
        app.add_exception_handler(
        subclass,
        _get_handler(subclass.status,subclass.__doc__)
    )
    @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)     #to handle internl server errors  
    def internal_server_error(request,exception):
     return JSONResponse(
        content = {"detail":"Something went wrong.."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR

    )


