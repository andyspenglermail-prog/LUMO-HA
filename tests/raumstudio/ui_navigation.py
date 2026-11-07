"""Real disclosure navigation only; no forced clicks or relaxed assertions."""
def room_action(page, selector):
    menu=page.locator('#room-selection-menu')
    if not menu.evaluate('e=>e.open'):menu.locator('summary').click()
    page.locator(selector).click()
    if menu.evaluate('e=>e.open'):menu.locator('summary').click()

def reveal_actions(row):
    menu=row.locator('.draft-actions').first
    if not menu.evaluate('e=>e.open'):menu.locator('summary').click()
    return row
