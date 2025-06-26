"""Uses the nftables library to validate a given nftables script"""
from re import findall
from nftables import Nftables

REGEX =  r"(?!Error: Could not process rule: Operation not permitted\n)(Error:.*\n)"
NFT = Nftables()

def validate_script(file:str):
    """Validates a given nftables script
    Returns:
        None if the script is a valid nftables-script
        errors, error otherwise [errors]: List of nft-syntax errors,[error]: Full string Error message as returned by nftables
    """
    NFT.set_dry_run(onoff='on')
    _, _, error = NFT.cmd_from_file(file)
    errors = findall(REGEX, error)

    if not errors:
        return None, None
    return errors, error
