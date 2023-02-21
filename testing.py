
pickaxe = "NilAxe"
ore = "Neptunium"
rarity = "Base Rarity: 1 in 16,000,000"
adjustedFound = False
with open('adjusted.txt', 'r') as adjustedRarities:
    for num, line in enumerate(adjustedRarities):
        if ore in line and not (' ' + ore) in line and not adjustedFound:
            rarity += "\nAdjusted Rarity: 1 in " + line.split()[-1]
            adjustedFound = True
if 'Hyperheated Quasar' in ore:
    if '57' in pickaxe:
        if 'Ionized' in ore:
            rarity += "\nAdjusted Rarity: 1 in 3,471,984,000"
        elif 'Spectral' in ore:
            rarity += "\nAdjusted Rarity: 1 in 52,079,760,000"
        else:
            rarity += "\nAdjusted Rarity: 1 in 86,799,600"
    else:
        if 'Ionized' in ore:
            rarity += "\nAdjusted Rarity: 1 in 347,198,400,000"
        elif 'Spectral' in ore:
            rarity += "\nAdjusted Rarity: 1 in 5,207,976,000,000"
        else:
            rarity += "\nAdjusted Rarity: 1 in 8,679,960,000"
print(rarity)
