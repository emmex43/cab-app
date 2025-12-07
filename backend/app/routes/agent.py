from flask import Blueprint, request, jsonify
import time

agent_bp = Blueprint('agent', __name__)


@agent_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '').lower()

    # Simulate "Thinking" time (0.5 seconds)
    time.sleep(0.5)

    reply = ""

    # 🧠 THE LOGIC (You can add more rules here)
    if "price" in user_msg or "cost" in user_msg or "how much" in user_msg:
        reply = "💰 PRICE LIST:\n• Shuttle (Main Gate, Small Gate, Back Gate): ₦100\n• Shuttle (New Benin, Ring Road, Uselu): ₦300\n• Cab (Anywhere on Campus): ₦200 flat rate."

    elif "location" in user_msg or "where" in user_msg or "pickup" in user_msg:
        reply = "📍 PICKUP POINTS:\n• Hall 2 Car Park\n• Small Gate Bus Stop\n• Faculty of Engineering Pack\n• Management Science Pack\n• Back Gate Close to Faculty of Arts."

    elif "safety" in user_msg or "safe" in user_msg:
        reply = "🛡️ SAFETY FIRST:\nAll UNIBEN Mobility drivers are verified students/staff. We track every ride in real-time for your security."

    elif "hello" in user_msg or "hi" in user_msg or "hey" in user_msg:
        reply = "👋 Hello! I am the UNIBEN Assistant. Ask me about prices, locations, or safety!"

    elif "thank" in user_msg:
        reply = "You're welcome! Safe travels. 🚕"

    else:
        reply = "I can help with Prices, Locations, and Safety. Try asking: 'How much is a cab?'"

    return jsonify({'reply': reply})
