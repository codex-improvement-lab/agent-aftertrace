def settle():
    balance = 20
    violation_seen = False
    for step in range(100):
        delta = 1
        if step == 47:
            delta = -100
        balance += delta
        if balance < 0:
            violation_seen = True
        if step == 48:
            balance = 20
    assert not violation_seen, "a negative balance was observed earlier"


settle()
