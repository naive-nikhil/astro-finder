from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import random
from math import log

# Planetary dignities
exaltation = {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
              "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"}
debilitation = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
                "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"}

# House mapping (Taurus Ascendant default)
house_map = {"Taurus": 1, "Gemini": 2, "Cancer": 3, "Leo": 4, "Virgo": 5, "Libra": 6,
             "Scorpio": 7, "Sagittarius": 8, "Capricorn": 9, "Aquarius": 10, "Pisces": 11, "Aries": 12}

# Sign qualities
sattvic_signs = ["Cancer", "Pisces", "Virgo", "Gemini"]
rajasic_signs = ["Aries", "Leo", "Libra", "Sagittarius"]
tamasic_signs = ["Taurus", "Scorpio", "Capricorn", "Aquarius"]

# Simulated training data
X_train = [
    [1, 0, 2, 15], [1, 0, 1, 10], [0, 0, 2, 20], [0, 0, 1, 25],
    [0, 0, 0, 5], [0, 1, 0, 10], [0, 1, 1, 15], [0, 0, 0, 20]
]
y_train = ["Very Strong", "Strong", "Strong", "Moderate", "Weak", "Very Weak", "Weak", "Moderate"]

# Train KNN model
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)

# Feature extraction
def get_features(planet, sign, degrees):
    is_exalted = 1 if planet in exaltation and exaltation[planet] == sign else 0
    is_debilitated = 1 if planet in debilitation and debilitation[planet] == sign else 0
    house = house_map[sign]
    house_strength = 2 if house in [1, 4, 7, 10] else 1 if house in [5, 9] else 0
    return [is_exalted, is_debilitated, house_strength, degrees]

# Word pools for dynamic text
adjectives_strong = ["radiant", "potent", "vibrant", "commanding", "stellar"]
adjectives_weak = ["dim", "faltering", "subdued", "strained", "fragile"]
verbs_strong = ["empowers", "uplifts", "drives", "enhances", "fortifies"]
verbs_weak = ["hampers", "restrains", "clouds", "weakens", "burdens"]
traits = {
    "Sun": ["authority", "vitality", "leadership"],
    "Moon": ["emotions", "intuition", "nurturing"],
    "Mars": ["energy", "courage", "ambition"],
    "Mercury": ["intellect", "communication", "wit"],
    "Jupiter": ["wisdom", "growth", "optimism"],
    "Venus": ["love", "beauty", "harmony"],
    "Saturn": ["discipline", "patience", "structure"],
    "Rahu": ["desire", "innovation", "intensity"],
    "Ketu": ["spirituality", "detachment", "insight"],
    "Uranus": ["innovation", "unpredictability", "change"],
    "Neptune": ["imagination", "mysticism", "dreams"],
    "Pluto": ["transformation", "power", "rebirth"]
}
house_contexts = {
    1: "self-expression", 4: "home life", 7: "partnerships", 10: "career",
    5: "creativity", 9: "higher learning", 6: "challenges", 8: "transformation", 12: "subconscious"
}

# Generate unique text
def generate_text(planet, strength, sign, degrees):
    house = house_map[sign]
    trait = random.choice(traits[planet])
    context = house_contexts.get(house, "life")
    
    if strength in ["Very Strong", "Strong"]:
        adj = random.choice(adjectives_strong)
        verb = random.choice(verbs_strong)
        if planet in exaltation and exaltation[planet] == sign:
            desc = f"In {sign}, {planet}’s {adj} essence {verb} your {trait}, shining through {context}."
        else:
            desc = f"{planet} weaves a {adj} thread in {sign}, {verb}ing your {trait} in {context}."
    else:
        adj = random.choice(adjectives_weak)
        verb = random.choice(verbs_weak)
        if planet in debilitation and debilitation[planet] == sign:
            desc = f"{planet} in {sign} carries a {adj} burden, {verb}ing your {trait} within {context}."
        else:
            desc = f"In {sign}, {planet}’s {adj} nature {verb} your {trait}, touching {context}."
    return desc

# Guna calculation (skip outer planets)
def calculate_gunas(kundli):
    guna_scores = {"Sattva": 0, "Rajas": 0, "Tamas": 0}
    guna_map = {
        "Jupiter": "Sattva", "Sun": "Sattva", "Moon": "Sattva",
        "Mercury": "Rajas", "Venus": "Rajas",
        "Mars": "Tamas", "Saturn": "Tamas", "Rahu": "Tamas", "Ketu": "Tamas"
    }
    
    for planet, details in kundli.items():
        if planet == "Ascendant" or planet in ["Uranus", "Neptune", "Pluto"]:  # Skip outer planets
            continue
        base_score = 10
        sign = details["Sign"]
        house = house_map[sign]
        
        if planet in ["Moon", "Jupiter"]:
            base_score += 5
        if planet == "Moon" and sign in sattvic_signs:
            base_score += 5
        
        if planet in exaltation and exaltation[planet] == sign:
            base_score += 4 if guna_map[planet] == "Sattva" else 3
        if planet in debilitation and debilitation[planet] == sign:
            base_score -= 2
        
        if house in [1, 5, 9, 11]:
            base_score += 5 if guna_map[planet] == "Sattva" else 2
        elif house in [4, 7, 10]:
            base_score += 3
        elif house in [6, 8, 12]:
            base_score -= 1
        
        if sign in sattvic_signs and guna_map[planet] == "Sattva":
            base_score += 3
        
        guna = guna_map[planet]
        guna_scores[guna] += max(0, base_score)
    
    if kundli["Ascendant"]["Sign"] in tamasic_signs:
        guna_scores["Sattva"] += 5
    
    total = sum(guna_scores.values())
    if total == 0:
        total = 1
    guna_percent = {k: round((v / total) * 100, 1) for k, v in guna_scores.items()}
    dominant_guna = max(guna_scores, key=guna_scores.get)
    varna_map = {"Sattva": "Brahmin", "Rajas": "Kshatriya", "Tamas": "Shudra"}
    guna_desc = (f"Gunas: Sattva {guna_percent['Sattva']}%, Rajas {guna_percent['Rajas']}%, "
                 f"Tamas {guna_percent['Tamas']}%. Dominant: {dominant_guna} ({varna_map[dominant_guna]}).")
    return guna_desc

# Rarity calculation
def get_rarity(kundli):
    rarity_score = 0
    
    exalted_count = sum(1 for p, d in kundli.items() if p in exaltation and exaltation[p] == d["Sign"])
    debilitated_count = sum(1 for p, d in kundli.items() if p in debilitation and debilitation[p] == d["Sign"])
    rarity_score += (exalted_count + debilitated_count) * 10
    
    rarity_score += 15
    
    sign_counts = {}
    for planet, details in kundli.items():
        if planet != "Ascendant":
            sign = details["Sign"]
            sign_counts[sign] = sign_counts.get(sign, 0) + 1
    for count in sign_counts.values():
        if count > 1:
            rarity_score += (count - 1) * 8
    
    house_counts = {i: 0 for i in range(1, 13)}
    for planet, details in kundli.items():
        if planet != "Ascendant":
            house_counts[house_map[details["Sign"]]] += 1
    variance = np.var(list(house_counts.values()))
    rarity_score += int(variance * 5)
    
    for p1, d1 in kundli.items():
        if p1 == "Ascendant":
            continue
        for p2, d2 in kundli.items():
            if p2 <= p1 or p2 == "Ascendant" or d1["Sign"] != d2["Sign"]:
                continue
            if abs(d1["Degrees"] - d2["Degrees"]) < 5:
                rarity_score += 10
    
    rarity_log = 100 * (1 - 1 / (1 + log(1 + rarity_score / 10)))
    rarity_percentage = min(100, max(0, int(rarity_log)))
    rarity_desc = f"Your Kundli’s celestial aura is {rarity_percentage}% rare, a unique cosmic fingerprint."
    return rarity_percentage, rarity_desc

# Main analysis function
def analyze_kundli(kundli):
    scores = {}
    for planet, details in kundli.items():
        if planet == "Ascendant" or planet in ["Uranus", "Neptune", "Pluto"]:
            continue  # Skip outer planets for strength (optional, kept for consistency)
        features = get_features(planet, details["Sign"], details["Degrees"])
        strength = knn.predict([features])[0]
        score = {"Very Strong": 10, "Strong": 7, "Moderate": 4, "Weak": 2, "Very Weak": 0}[strength]
        scores[planet] = (score, strength)
    
    strongest_planet = max(scores, key=lambda k: scores[k][0])
    weakest_planet = min(scores, key=lambda k: scores[k][0])
    
    strong_text = generate_text(strongest_planet, scores[strongest_planet][1], 
                                kundli[strongest_planet]["Sign"], kundli[strongest_planet]["Degrees"])
    weak_text = generate_text(weakest_planet, scores[weakest_planet][1], 
                              kundli[weakest_planet]["Sign"], kundli[weakest_planet]["Degrees"])
    
    rarity_score, rarity_text = get_rarity(kundli)
    guna_text = calculate_gunas(kundli)
    
    return strongest_planet, strong_text, weakest_planet, weak_text, rarity_text, guna_text