def local_login():
    """Simulate local login with username and password."""
    # Define valid credentials (username and password)
    valid_username = "admin"
    valid_password = "123"

    print("Please login to continue.")
    username = input("Username: ")
    password = input("Password: ")

    if username == valid_username and password == valid_password:
        print("Login successful!")
        return True
    else:
        print("Invalid credentials. Please try again.")
        return False