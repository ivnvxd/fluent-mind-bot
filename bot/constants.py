# State definitions for top level conversation
SELECTING_SETTING, MODEL_PARAMETERS, MEMORY_SETTINGS = map(chr, range(3))

LANGUAGE_MODEL, TEMPERATURE, MAXIMUM_TOKENS = map(chr, range(3, 6))

MEMORY_ENABLE, MEMORY_SIZE = map(chr, range(6, 8))

# Meta states
BACK, S = map(chr, range(8, 10))

HELP_MESSAGE = """Available commands:
⚙️ /settings — Change GPT-3 settings
❓ /help — Show help
📈 /stat — Show usage statistics
💾 /memo — Show current context
🆕 /new — Start new dialog
🔄 /retry — Regenerate last bot answer
"""
