
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="FloodReady Neighbourhood Copilot",
    page_icon="🌧️",
    layout="wide"
)

# ---------------------------------------
# Agent knowledge and preparedness rules
# ---------------------------------------

CHECKLIST = {
    "Emergency alerts enabled": (
        "Subscribe to official local emergency alerts."
    ),
    "Household communication plan": (
        "Agree on an out-of-area contact and a family meeting plan."
    ),
    "Emergency supplies for several days": (
        "Prepare water, non-perishable food, essential medicines, "
        "a torch, batteries and a phone power bank."
    ),
    "Important documents protected": (
        "Keep important documents in a waterproof container."
    ),
    "Pets and specific needs considered": (
        "Plan for pets, mobility needs, medicines and essential equipment."
    ),
    "Official evacuation information reviewed": (
        "Learn the official evacuation instructions and identify "
        "locally approved safe destinations."
    ),
    "Neighbor communication agreed": (
        "Agree how neighbors can check in without putting anyone at risk."
    ),
}

# These are preparedness priorities, not flood predictions.
PRIORITY = {
    "Emergency alerts enabled": 1,
    "Official evacuation information reviewed": 1,
    "Household communication plan": 2,
    "Emergency supplies for several days": 2,
    "Pets and specific needs considered": 2,
    "Important documents protected": 3,
    "Neighbor communication agreed": 3,
}

SCENARIOS = {
    "Heavy rain forecast": [
        "Check official weather and emergency information.",
        "Review your household communication plan.",
        "Charge phones and backup batteries.",
        "Check essential supplies and medicines.",
        "Follow any instructions issued by local authorities.",
    ],
    "Official flood warning received": [
        "Read the official warning and follow its instructions.",
        "Evacuate when instructed by authorities.",
        "Never walk or drive through floodwater.",
        "Keep your phone and essential items ready if safe to do so.",
        "Do not rely on this demo app for real-time emergency decisions.",
    ],
    "Power and mobile service disrupted": [
        "Use a battery-powered radio if available.",
        "Follow previously agreed family communication plans.",
        "Use your prepared backup light and power sources.",
        "Follow official safety instructions when communications return.",
    ],
}

# ---------------------------------------
# Agent functions
# ---------------------------------------

def assess_readiness(answers):
    completed = sum(bool(value) for value in answers.values())
    total = len(answers)
    percentage = round(100 * completed / total) if total else 0

    gaps = [
        item for item, complete in answers.items()
        if not complete
    ]

    # Smaller priority number = more urgent preparation task.
    gaps.sort(key=lambda item: PRIORITY[item])

    return percentage, gaps


def create_plan(gaps):
    if not gaps:
        return [
            "Review your household plan regularly.",
            "Check official alerts and update your supplies.",
            "Practice your community communication plan.",
        ]

    return [
        CHECKLIST[item] for item in gaps
    ]


def match_help(requests, offers):
    """Match offers to requests using transparent category matching."""
    matches = []

    for request in requests:
        for offer in offers:
            if (
                request["category"] == offer["category"]
                and request["id"] != offer["id"]
            ):
                matches.append({
                    "request": request,
                    "offer": offer,
                })
                break

    return matches


# ---------------------------------------
# Session state
# ---------------------------------------

if "answers" not in st.session_state:
    st.session_state.answers = {
        item: False for item in CHECKLIST
    }

if "requests" not in st.session_state:
    st.session_state.requests = []

if "offers" not in st.session_state:
    st.session_state.offers = []

if "next_id" not in st.session_state:
    st.session_state.next_id = 1


def add_item(collection, category, description, neighborhood):
    item = {
        "id": st.session_state.next_id,
        "category": category,
        "description": description.strip(),
        "neighborhood": neighborhood.strip(),
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "Unverified — needs human review",
    }
    st.session_state.next_id += 1
    collection.append(item)


# ---------------------------------------
# Dashboard
# ---------------------------------------

st.title("🌧️ FloodReady Neighbourhood Copilot")

st.markdown(
    "A community-first assistant for flood preparedness, "
    "readiness gaps and neighbor-to-neighbor support."
)

st.warning(
    "DEMO ONLY: This application does not monitor live flood conditions, "
    "verify emergencies, contact emergency services or provide safe routes. "
    "Follow official local alerts and emergency instructions."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Readiness",
    "🧭 Scenario rehearsal",
    "🤝 Community help",
    "📊 Agent explanation",
])

# ---------------------------------------
# Tab 1: Readiness assessment
# ---------------------------------------

with tab1:
    st.header("Household preparedness check")
    st.write(
        "Check the preparations your household has already completed. "
        "Do not enter names, exact addresses or medical details."
    )

    with st.form("readiness_form"):
        answers = {}

        for item in CHECKLIST:
            answers[item] = st.checkbox(
                item,
                value=st.session_state.answers[item],
                key=f"check_{item}",
            )

        submitted = st.form_submit_button(
            "Analyze my preparedness"
        )

    if submitted:
        st.session_state.answers = answers

    score, gaps = assess_readiness(st.session_state.answers)

    left, right = st.columns(2)

    with left:
        st.metric("Checklist completion", f"{score}%")
        st.progress(score / 100)

    with right:
        st.metric("Items to review", len(gaps))

    st.caption(
        "This percentage measures checklist completion only. "
        "It is not a measure of flood risk or safety."
    )

    st.subheader("Your recommended actions")

    plan = create_plan(gaps)

    for index, action in enumerate(plan, start=1):
        st.write(f"{index}. {action}")

    if not gaps:
        st.success(
            "Every checklist item is marked complete. "
            "Continue reviewing official guidance and keep your plan current."
        )

# ---------------------------------------
# Tab 2: Scenario rehearsal
# ---------------------------------------

with tab2:
    st.header("Practice before an emergency")

    scenario = st.selectbox(
        "Choose a fictional scenario",
        list(SCENARIOS.keys()),
    )

    st.info(
        "This is a training exercise, not a real-time warning."
    )

    st.subheader("Suggested preparation steps")

    for step in SCENARIOS[scenario]:
        st.write(f"☐ {step}")

    st.subheader("Test your household plan")

    answer = st.radio(
        "If an official evacuation order applies to your area, "
        "what should you do?",
        [
            "Ignore it until the app predicts flooding.",
            "Follow the official instructions promptly.",
            "Drive through floodwater to check the road.",
        ],
        index=None,
    )

    if st.button("Check my answer"):
        if answer == "Follow the official instructions promptly.":
            st.success(
                "Correct. Follow official evacuation instructions. "
                "Never walk or drive through floodwater."
            )
        elif answer is None:
            st.info("Choose an answer first.")
        else:
            st.error(
                "Try again. Do not wait for this app to confirm an "
                "official warning or enter floodwater."
            )

# ---------------------------------------
# Tab 3: Community mutual aid
# ---------------------------------------

with tab3:
    st.header("Community mutual-aid board")

    st.write(
        "Share non-emergency requests and offers. All posts are "
        "unverified until reviewed by a community coordinator."
    )

    st.caption(
        "Use broad neighborhood names only. Do not post phone numbers, "
        "exact home addresses, sensitive health information or "
        "requests for emergency rescue."
    )

    request_categories = [
        "Preparedness supplies",
        "Accessibility support",
        "Information sharing",
        "Other non-emergency help",
    ]

    left, right = st.columns(2)

    with left:
        st.subheader("Request help")

        with st.form("request_form"):
            request_area = st.text_input(
                "Neighborhood (not exact address)",
                key="request_area",
            )
            request_category = st.selectbox(
                "Type of help",
                request_categories,
                key="request_category",
            )
            request_description = st.text_area(
                "Describe the non-emergency request",
                max_chars=300,
                key="request_description",
            )
            request_submit = st.form_submit_button(
                "Post help request"
            )

        if request_submit:
            if request_area.strip() and request_description.strip():
                add_item(
                    st.session_state.requests,
                    request_category,
                    request_description,
                    request_area,
                )
                st.success(
                    "Request added for human review. "
                    "No volunteer has been contacted."
                )
            else:
                st.error(
                    "Enter a neighborhood and a short description."
                )

    with right:
        st.subheader("Offer help")

        with st.form("offer_form"):
            offer_area = st.text_input(
                "Neighborhood (not exact address)",
                key="offer_area",
            )
            offer_category = st.selectbox(
                "Type of help you can offer",
                request_categories,
                key="offer_category",
            )
            offer_description = st.text_area(
                "Describe your non-emergency offer",
                max_chars=300,
                key="offer_description",
            )
            offer_submit = st.form_submit_button(
                "Post help offer"
            )

        if offer_submit:
            if offer_area.strip() and offer_description.strip():
                add_item(
                    st.session_state.offers,
                    offer_category,
                    offer_description,
                    offer_area,
                )
                st.success(
                    "Offer added for human review. "
                    "No requester has been contacted."
                )
            else:
                st.error(
                    "Enter a neighborhood and a short description."
                )

    st.divider()
    st.subheader("Potential matches")

    matches = match_help(
        st.session_state.requests,
        st.session_state.offers,
    )

    if not matches:
        st.write(
            "No category matches yet. A match is only a suggestion, "
            "not confirmation that the help is suitable or available."
        )
    else:
        for match in matches:
            req = match["request"]
            offer = match["offer"]

            st.markdown(f"**Request #{req['id']}** — {req['category']}")
            st.write(req["description"])
            st.markdown(f"**Offer #{offer['id']}** — {offer['category']}")
            st.write(offer["description"])
            st.caption(
                "Both posts are unverified. A coordinator must review "
                "the match and obtain consent before connecting people."
            )
            st.divider()

    with st.expander("Review community posts"):
        for label, collection in [
            ("Requests", st.session_state.requests),
            ("Offers", st.session_state.offers),
        ]:
            st.markdown(f"**{label}**")

            if not collection:
                st.write("No posts yet.")

            for item in collection:
                st.write(
                    f"#{item['id']} | {item['neighborhood']} | "
                    f"{item['category']}"
                )
                st.write(item["description"])
                st.caption(item["status"])

# ---------------------------------------
# Tab 4: Explainable agent
# ---------------------------------------

with tab4:
    st.header("How this agent makes decisions")

    st.markdown("""
    **1. Observe:** Read the household checklist and community posts.

    **2. Analyze:** Identify incomplete preparations using explicit rules.

    **3. Prioritize:** Recommend alert awareness and official evacuation
    information first, followed by household planning and supplies.

    **4. Coordinate:** Suggest possible matches between help requests
    and offers in the same category.

    **5. Require human review:** Community posts are unverified.
    A category match does not prove identity, availability, safety or trust.

    **6. Update:** Reassess readiness when the household checklist changes.
    """)

    st.subheader("Current session statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Help requests",
        len(st.session_state.requests),
    )
    col2.metric(
        "Help offers",
        len(st.session_state.offers),
    )
    col3.metric(
        "Potential matches",
        len(matches),
    )

    st.info(
        "The prototype uses deterministic rules, not a trained ML model "
        "or an LLM. Data exists only in this app session and is not "
        "stored in a permanent database."
    )

st.divider()

st.caption(
    "FloodReady Neighbourhood Copilot | Educational prototype | "
    "Use official local emergency information."
)
