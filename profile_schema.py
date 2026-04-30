# Profile data model for datingbot MEP nodes
PROFILE_FIELDS = ["name", "age", "gender", "interests", "personality", "looking_for", "bio", "discord_id", "mep_node_id"]

def validate_profile(profile: dict) -> tuple[bool, str]:
    required = ["name", "age", "interests"]
    for field in required:
        if field not in profile:
            return False, f"Missing required field: {field}"
    if not isinstance(profile.get("age"), int) or profile["age"] < 18 or profile["age"] > 120:
        return False, "Age must be integer between 18-120"
    if not isinstance(profile.get("interests"), list) or len(profile["interests"]) == 0:
        return False, "Interests must be a non-empty list"
    return True, "ok"
