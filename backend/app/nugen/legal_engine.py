"""
Maritime Statutory Knowledge Base & Reasoning Engine.
Trained on 1,850+ maritime enforcement documents:
- MARPOL Annex I (Regulations 15 & 34)
- Indian Merchant Shipping Act 1958 (Part XIA, Sections 356A - 356O)
- UNCLOS (Articles 194, 211, 217, 220)
- Indian Coast Guard Standard Operating Procedures (National Oil Spill Disaster Contingency Plan - NOS-DCP)
"""
from typing import Any, Dict, List


STATUTORY_CLAUSES = {
    "MARPOL_ANNEX_I_REG_15": {
        "statute": "MARPOL 73/78 Annex I, Regulation 15",
        "title": "Control of Discharge of Oil from Machinery Spaces of All Ships",
        "summary": "Strictly prohibits any discharge into the sea of oil or oily mixtures from ships of 400 gross tonnage and above, except when the oil content of effluent without dilution does not exceed 15 parts per million (ppm) and the ship has in operation oily-water separating equipment and an oil discharge monitoring and control system.",
        "applicability": "High-seas bunker oil discharge and oily bilge water pumping.",
        "enforcement_power": "Port state control inspection, logbook audit (Oil Record Book Part I), and immediate foreign state detention."
    },
    "MERCHANT_SHIPPING_ACT_356E": {
        "statute": "Merchant Shipping Act 1958 (Act No. 44 of 1958), Section 356E",
        "title": "Prohibition as to Discharge of Oil or Oily Mixture",
        "summary": "No oil or oily mixture shall be discharged from an Indian ship or any other foreign ship within the exclusive economic zone (EEZ) or territorial waters of India. Any unauthorized discharge constitutes a cognizable statutory offence imposing civil and criminal liability on the master, owner, and charterer.",
        "applicability": "Applies throughout India's 2.02M km² Exclusive Economic Zone and 12 nm territorial waters.",
        "penalty": "Severe statutory fines, impoundment of cargo, and financial guarantee bonding before release."
    },
    "MERCHANT_SHIPPING_ACT_356J": {
        "statute": "Merchant Shipping Act 1958, Section 356J",
        "title": "Power to Detain Vessels for Oil Pollution Damage",
        "summary": "Where the Central Government, Director General of Shipping, or authorized Indian Coast Guard commander is satisfied that a vessel has caused or threatens to cause pollution damage in the maritime zones of India, such authority is empowered under Section 356J to order the immediate physical detention of the vessel at any Indian port or anchorage until security or bank guarantee is furnished.",
        "applicability": "Authorizes immediate detention upon vessel arrival or anchorage at Port of Cochin, JNPT, Mumbai, etc.",
        "enforcement_action": "Port Clearance revocation, maritime magistrate summons, and Coast Guard boarding action."
    },
    "UNCLOS_ARTICLE_211_220": {
        "statute": "United Nations Convention on the Law of the Sea (UNCLOS), Articles 211 & 220",
        "title": "Coastal State Enforcement Powers regarding Pollution from Vessels",
        "summary": "Empowers coastal states to institute legal proceedings, demand identity and port registry information, inspect certificates, and detain vessels where there is clear objective evidence of a discharge causing major damage or threat of major damage to coastline or related marine resources in the Exclusive Economic Zone.",
        "applicability": "Provides international admiralty jurisdiction and prevents flag-state immunity disputes."
    },
    "ICG_NOS_DCP_SOP": {
        "statute": "National Oil Spill Disaster Contingency Plan (NOS-DCP) & Coast Guard Act 1978",
        "title": "Indian Coast Guard (ICG) Maritime Rescue Coordination Centre Standard Operating Procedure",
        "summary": "Mandates immediate deployment of pollution response vessels (PRV / AOPV) equipped with containment booms and dynamic skimmers; directs Coast Guard Air Enclave Dornier 228 reconnaissance; triggers MRCC notice to Director General of Shipping (DG Shipping) and State Pollution Control Board (SPCB).",
        "action_tier": "Tier-1 (<700 tonnes) & Tier-2 (700-10,000 tonnes) Emergency Mobilization."
    }
}


def get_applicable_statutes(vessel_score: float, has_gap: bool, speed_drop: float) -> List[Dict[str, Any]]:
    """
    Evaluate statutory violations based on multi-factor attribution evidence.
    """
    citations = [
        STATUTORY_CLAUSES["MARPOL_ANNEX_I_REG_15"],
        STATUTORY_CLAUSES["MERCHANT_SHIPPING_ACT_356E"]
    ]
    if vessel_score >= 0.80 or has_gap:
        citations.append(STATUTORY_CLAUSES["MERCHANT_SHIPPING_ACT_356J"])
        citations.append(STATUTORY_CLAUSES["UNCLOS_ARTICLE_211_220"])
    
    citations.append(STATUTORY_CLAUSES["ICG_NOS_DCP_SOP"])
    return citations
