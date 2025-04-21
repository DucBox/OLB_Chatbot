from compdfkit.client import CPDFClient
from compdfkit.enums import CPDFConversionEnum
from compdfkit.param import CPDFToTxtParameter
from compdfkit.constant import CPDFConstant

from src.utils.config import public_key, secret_key


client = CPDFClient(public_key, secret_key)