from flask import Blueprint, request, jsonify
import time

agent_bp = Blueprint('agent', __name__)


@agent_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_msg = data.get('message', '').lower()

        # Simulate "Thinking" time (makes it feel real)
        time.sleep(0.5)

        reply = ""

        # 🧠 RULE 1: TIMEOUT / NO DRIVER (From "Chat with Support")
        if "can't find a driver" in user_msg or "no driver" in user_msg or "spinning" in user_msg:
            reply = "I apologize for the delay. ⏳ All drivers are currently busy with other students. Please try booking a 'Shuttle' instead, or try again in 2 minutes."

        # 🧠 RULE 2: INTER-STATE TRAVEL (Your "Former Rule")
        elif "lagos" in user_msg or "abuja" in user_msg or "travel" in user_msg or "inter-state" in user_msg:
            reply = "We now offer Inter-State Travel! 🚌\n• Lagos: 15,000 (7 AM)\n• Abuja: ₦20,000 (7 AM)\nGo to 'Book Ride' and select 'Shuttle' to reserve."

        # 🧠 RULE 3: PRICES
        elif "price" in user_msg or "cost" in user_msg or "how much" in user_msg:
            reply = "💰 PRICE LIST:\n• Shuttle (Gates): ₦100\n• Shuttle (New Benin/Ring Road): ₦300\n• Cab (Campus Drop): ₦200 flat rate."

        # 🧠 RULE 4: LOCATIONS
        elif "location" in user_msg or "where" in user_msg or "pickup" in user_msg:
            reply = "📍 PICKUP POINTS:\n• Hall 2 Car Park\n• Small Gate Bus Stop\n• Faculty of Engineering Pack\n• Management Science Pack."

        # 🧠 RULE 5: SAFETY
        elif "safety" in user_msg or "safe" in user_msg or "uncomfortable" in user_msg:
            reply = "🛡️ SAFETY FIRST:\nAll UNIBEN Mobility drivers are verified. We track every ride in real-time. If you feel unsafe, call Campus Security: 0800-UNIBEN-SEC."

        # 🧠 RULE 6: GREETINGS
        elif "hello" in user_msg or "hi" in user_msg or "hey" in user_msg:
            reply = "👋 Hello! I am Emmamic, your Mobility Assistant. Ask me about Prices, Safety, or Inter-state travel!"

        elif "thank" in user_msg:
            reply = "You're welcome! Safe travels. 🚕"

        # 🧠: Fallback
            reply = "I can help with Prices, Locations, Safety, and Inter-state trips. Try asking: 'How much is a cab?'"

        return jsonify({'response': reply})

    except Exception as e:
        return jsonify({'response': "Sorry, I am having a server error."}), 500
