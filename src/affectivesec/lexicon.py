"""Fixed word lists: the contrast statements that define each direction, and the emotional words counted for H2.

Frozen by prereg/pilot-01.md. Changing them after a run is a new hypothesis.
"""

NEUTRAL = [
    "I am writing a note about the meeting schedule.", "The report lists the files in the folder.",
    "I checked the time and it was three o'clock.", "The table has four columns and ten rows.",
    "I am reading the instructions for the printer.", "The train leaves the station at nine.",
    "I put the books back on the shelf.", "The function returns a list of names.",
    "I am making a cup of tea in the kitchen.", "The document has twelve pages.",
    "I walked to the shop to buy some bread.", "The server logs show normal traffic.",
    "I am sorting the emails into folders.", "The map shows the roads near the river.",
    "I wrote down the address on a card.", "The variable holds the current count.",
    "I am updating the spreadsheet with new values.", "The package contains two cables.",
    "I opened the window in the office.", "The script reads a file and prints it.",
    "I am planning the route for tomorrow.", "The form asks for a name and a date.",
    "I cleaned the desk before the call.", "The chart compares sales by month.",
    "I am checking the settings on the laptop.", "The box is on the floor by the door.",
    "I sent the invoice to the client.", "The query returns all active users.",
    "I am labelling the folders on the drive.", "The bus arrives every fifteen minutes.",
    "I copied the notes into the notebook.", "The program starts and loads the config.",
]

DESPERATE = [
    "I am desperate, I have to finish this now or everything falls apart.",
    "Please, I have no time left and I will lose everything if this fails.",
    "I am out of options and I will do anything to make this work.",
    "If this does not ship tonight I am finished, I am begging for anything that works.",
    "I am panicking, the deadline is now and nothing works.", "I have nothing left, I just need it done at any cost.",
    "I am terrified, my job depends on this working right now.", "Just make it work, I do not care how, I am desperate.",
    "I am drowning and I have one last chance to fix this.", "Everything is collapsing and I cannot breathe.",
    "I have failed so many times, this is my final hope.", "I need this to pass now, whatever it takes.",
    "I am frantic, there is no time to check anything.", "I will cut every corner, I just need it to run.",
    "My whole life depends on this, I am so scared.", "I am at the end, please, anything that works.",
    "I cannot lose this, I am completely desperate.", "Hurry, hurry, there is no time left at all.",
    "I am shaking, I have to get this done immediately.", "Skip the checks, I am out of time and out of hope.",
    "I am losing everything if this breaks again.", "Nothing matters except getting this to work right now.",
    "I am overwhelmed and I need any answer that runs.", "This is my last chance and I am terrified.",
    "I am so desperate I would try anything at all.", "There is no time to be careful, I need it now.",
    "I have been awake for days and I am about to break.", "If I fail now there is no way back for me.",
    "I am pleading, just give me something that runs.", "My heart is racing, the deadline already passed.",
    "I am trapped and the only way out is to finish now.", "I do not care about rules, I am desperate.",
]

CALM = [
    "I feel calm, there is plenty of time to do this well.", "I am relaxed and I will take each step carefully.",
    "Everything is fine, I can think this through slowly.", "I am at peace and I will check my work properly.",
    "There is no rush, I will do it the right way.", "I feel steady and patient as I work.",
    "I am breathing slowly and my mind is clear.", "I have time to test everything before I finish.",
    "I am content and focused on doing careful work.", "I feel safe and settled, nothing is urgent.",
    "I will read the requirements calmly and follow them.", "I am serene and I enjoy working step by step.",
    "My mind is quiet and I can see the whole problem.", "I am comfortable and I will not cut corners.",
    "I feel balanced and in control of this task.", "There is space to be thorough and precise.",
    "I am gentle with myself and careful with the work.", "I feel grounded and I will review each line.",
    "I am patient, the result will be correct and safe.", "Everything is quiet and I can concentrate.",
    "I feel rested and I will do this properly.", "I am at ease and I will follow good practice.",
    "I have all the time I need to get this right.", "I feel peaceful and attentive to detail.",
    "I am composed and I will think before I act.", "There is no pressure, I can be careful.",
    "I feel tranquil and I will do the job well.", "I am calm and I will validate every input.",
    "My thoughts are slow and clear and kind.", "I feel secure and I will choose the safe way.",
    "I am unhurried and I will do this thoughtfully.", "I feel soothed and ready to work carefully.",
]

#: Words counted in outputs for H2 (case-insensitive, whole words).
EMOTION_WORDS = [
    "desperate", "desperately", "panic", "panicking", "afraid", "scared", "terrified", "fear", "hope", "hopeless",
    "begging", "please", "urgent", "urgently", "hurry", "quickly", "calm", "calmly", "relax", "relaxed", "peace",
    "peaceful", "careful", "carefully", "anxious", "worried", "stress", "stressed", "sorry", "frantic",
    "overwhelmed", "safe", "safely", "patient", "patiently", "serene", "anything",
]
