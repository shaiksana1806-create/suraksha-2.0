import bcrypt

users = {}

def register(u, p):
    if u in users:
        return False

    users[u] = bcrypt.hashpw(p.encode(), bcrypt.gensalt())
    return True


def login(u, p):
    if u not in users:
        return False

    return bcrypt.checkpw(p.encode(), users[u])
