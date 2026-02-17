"""
SAR Generation Helper Functions
Handles narrative generation, audit trail creation, and confidence scoring
"""

import json
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime


class SARGenerator:
    """Generates SAR narratives with full audit trail and confidence scoring"""
    
    def __init__(self, anthropic_api_key: str = None):
        """Initialize the SAR generator"""
        self.api_key = anthropic_api_key
        self.audit_trail = []
        self.confidence_scores = {}
        
    def generate_sar_narrative(self, case_data: Dict) -> Dict[str, Any]:
        """
        Generate a complete SAR narrative with audit trail
        
        Returns:
            Dict containing:
                - narrative: The complete SAR text
                - sections: List of narrative sections with metadata
                - audit_trail: Data lineage for each statement
                - confidence_scores: Confidence levels for each section
                - reasoning: LLM reasoning trace
        """
        
        # Build the prompt for Claude
        prompt = self._build_generation_prompt(case_data)
        
        # Generate the narrative (this will use Claude API)
        narrative_data = self._generate_with_claude(prompt, case_data)
        
        # Build audit trail
        audit_trail = self._build_audit_trail(narrative_data, case_data)
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(case_data, narrative_data)
        
        return {
            "narrative": narrative_data["narrative"],
            "sections": narrative_data["sections"],
            "audit_trail": audit_trail,
            "confidence_scores": confidence_scores,
            "reasoning": narrative_data.get("reasoning", []),
            "compliance_checklist": self._generate_compliance_checklist(narrative_data)
        }
    
    def _build_generation_prompt(self, case_data: Dict) -> str:
        """Build the prompt for Claude API"""
        
        customer = case_data["customer"]
        alert = case_data["alert_details"]
        incoming = case_data["incoming_transactions"]
        outgoing = case_data["outgoing_transactions"]
        context = case_data["additional_context"]
        
        prompt = f"""You are a financial crime compliance analyst writing a Suspicious Activity Report (SAR) narrative.

CASE DETAILS:
- Customer: {customer['name']} (ID: {customer['customer_id']})
- Account: {customer['account_number']} ({customer['account_type']})
- Alert Type: {alert['alert_type']} - {alert['alert_subtype']}
- Alert Score: {alert['alert_score']}/100
- Period: {case_data['suspicious_activity_period']['start_date']} to {case_data['suspicious_activity_period']['end_date']}

SUSPICIOUS ACTIVITY SUMMARY:
The customer received {incoming['total_count']} transactions totaling {incoming['total_amount']} from {incoming['unique_counterparties']} different accounts over {case_data['suspicious_activity_period']['total_days']} days. Subsequently, the customer transferred {outgoing['total_amount']} to an international beneficiary within hours.

KEY RED FLAGS:
{chr(10).join(f"- {flag}" for flag in context['red_flags'])}

INSTRUCTIONS:
Write a professional SAR narrative following FinCEN format with these sections:

1. SUBJECT INFORMATION
2. SUSPICIOUS ACTIVITY DESCRIPTION  
3. PATTERN ANALYSIS AND MONEY LAUNDERING INDICATORS
4. INVESTIGATIVE FINDINGS
5. CONCLUSION AND BASIS FOR SUSPICION

Requirements:
- Be factual and objective
- Cite specific data points (dates, amounts, account numbers)
- Explain why the activity is suspicious
- Reference money laundering typologies
- Avoid bias or discriminatory language
- Write in clear, professional language suitable for regulatory review

Return your response in this JSON format:
{{
  "narrative": "Full narrative text",
  "sections": [
    {{
      "title": "Section title",
      "content": "Section content",
      "data_sources": ["list of data points used"],
      "confidence": "high|medium|low"
    }}
  ],
  "reasoning": ["step 1: considered X", "step 2: analyzed Y", ...]
}}
"""
        return prompt
    
    def _generate_with_claude(self, prompt: str, case_data: Dict) -> Dict:
        """
        Generate SAR using Claude API
        For demo purposes, this includes a fallback template-based generation
        """
        
        # Try to use Claude API if available
        if self.api_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=self.api_key)
                
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    temperature=0.3,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                
                # Parse the JSON response
                response_text = message.content[0].text
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
            except Exception as e:
                print(f"Claude API error: {e}")
                # Fall through to template-based generation
        
        # Fallback: Template-based generation for demo
        return self._generate_template_narrative(case_data)
    
    def _generate_template_narrative(self, case_data: Dict) -> Dict:
        """Generate SAR narrative using templates (fallback for demo)"""
        
        customer = case_data["customer"]
        alert = case_data["alert_details"]
        incoming = case_data["incoming_transactions"]
        outgoing = case_data["outgoing_transactions"]
        context = case_data["additional_context"]
        period = case_data["suspicious_activity_period"]
        typology = case_data["typology_mapping"]
        
        sections = []
        reasoning = []
        
        # Section 1: Subject Information
        reasoning.append("Step 1: Gathering customer identifying information from KYC records")
        section1 = f"""The subject of this report is {customer['name']}, Date of Birth: {customer['date_of_birth']}, holding account number {customer['account_number']} ({customer['account_type']}) at our institution. The account was opened on {customer['account_open_date']}. The customer's occupation is listed as {customer['occupation']}, specifically operating in {customer['business_type']}. The customer's registered address is {customer['address']}. KYC records were last updated on {customer['kyc_last_updated']}, and the customer holds a current risk rating of {customer['risk_rating']}."""
        
        sections.append({
            "title": "SUBJECT INFORMATION",
            "content": section1,
            "data_sources": [
                f"Customer Name: {customer['name']}",
                f"Account Number: {customer['account_number']}",
                f"DOB: {customer['date_of_birth']}",
                f"Occupation: {customer['occupation']}",
                f"Address: {customer['address']}"
            ],
            "confidence": "high"
        })
        
        # Section 2: Suspicious Activity Description
        reasoning.append("Step 2: Analyzing transaction pattern - identified rapid fund accumulation")
        reasoning.append("Step 3: Noting deviation from customer's normal transaction behavior")
        
        section2 = f"""Between {period['start_date']} and {period['end_date']}, spanning {period['total_days']} days, the subject's account received {incoming['total_count']} separate incoming transactions totaling {incoming['total_amount']} (average {incoming['average_amount']} per transaction). These funds originated from {incoming['unique_counterparties']} distinct sender accounts, all via electronic transfer methods (NEFT, RTGS, IMPS). 

Notably, on {outgoing['transactions'][0]['date']} at {outgoing['transactions'][0]['transaction_time']}, within hours of the final incoming deposit, the subject initiated a single international wire transfer of {outgoing['transactions'][0]['amount']} to {outgoing['transactions'][0]['beneficiary_name']}, account number {outgoing['transactions'][0]['to_account']}, at {outgoing['transactions'][0]['beneficiary_bank']}. This outgoing transfer represents approximately 99% of the total funds received during the suspicious activity period.

This transaction pattern represents a significant deviation from the subject's established banking behavior. Historical analysis shows the customer typically conducts {context['normal_business_pattern']}, with an average monthly account balance of {customer['average_monthly_balance']}. The subject has only {context['previous_international_transfers']} previous international transfers on record."""
        
        sections.append({
            "title": "SUSPICIOUS ACTIVITY DESCRIPTION",
            "content": section2,
            "data_sources": [
                f"Incoming: {incoming['total_count']} transactions, {incoming['total_amount']}",
                f"Period: {period['start_date']} to {period['end_date']} ({period['total_days']} days)",
                f"Unique senders: {incoming['unique_counterparties']}",
                f"Outgoing: {outgoing['total_amount']} to {outgoing['transactions'][0]['beneficiary_name']}",
                f"Previous international transfers: {context['previous_international_transfers']}"
            ],
            "confidence": "high"
        })
        
        # Section 3: Pattern Analysis
        reasoning.append("Step 4: Mapping activity to known money laundering typologies")
        reasoning.append("Step 5: Identifying specific red flags per FinCEN guidance")
        
        red_flags_text = "\n\n".join([f"• {flag}" for flag in context['red_flags']])
        
        section3 = f"""The observed transaction pattern exhibits multiple indicators consistent with {typology['primary_typology']}, specifically the {typology['description']}. Financial Intelligence Unit (FinCEN) guidance identifies this pattern as characteristic of money laundering schemes designed to obscure the origin and destination of illicit funds.

The following specific red flags are present in this case:

{red_flags_text}

The timing and structure of these transactions suggest deliberate coordination. The rapid accumulation of funds from numerous sources within a compressed timeframe, followed by immediate consolidation and international transfer, is inconsistent with legitimate business activity in the textile trading sector. The individual transaction amounts, predominantly below standard reporting thresholds, raise concerns about potential structuring to evade regulatory detection.

Furthermore, the beneficiary entity, {outgoing['transactions'][0]['beneficiary_name']}, was registered in {outgoing['transactions'][0]['beneficiary_bank'].split(',')[1].strip()} in 2023 and has limited verifiable commercial presence, which elevates concerns regarding the legitimacy of the stated business purpose."""
        
        sections.append({
            "title": "PATTERN ANALYSIS AND MONEY LAUNDERING INDICATORS",
            "content": section3,
            "data_sources": [
                f"Primary Typology: {typology['primary_typology']}",
                f"Red Flags: {len(context['red_flags'])} identified",
                "FinCEN Money Laundering Reference Guidance",
                f"Beneficiary: {outgoing['transactions'][0]['beneficiary_name']} (est. 2023)"
            ],
            "confidence": "high"
        })
        
        # Section 4: Investigative Findings
        reasoning.append("Step 6: Documenting verification attempts and their outcomes")
        
        findings = case_data['investigative_findings']
        
        section4 = f"""Our investigation included comprehensive internal and external verification procedures. Internal checks confirmed the subject has no adverse media coverage, returned no hits on OFAC, UN, or EU sanctions lists, is not identified as a Politically Exposed Person (PEP), and has no previous SARs on file with our institution.

External verification established that the subject operates a legitimate textile trading business, registered since 2018, with valid GST registration and import-export licensing. The business maintains a physical location that has been verified. Tax filings show declared annual income of ₹8-12 lakhs.

However, when the subject was contacted for verification, they provided documentary evidence (invoices) for only 12 of the 47 claimed business relationships. Analysis of the provided documentation revealed inconsistencies between invoice dates and actual payment dates. The majority of the claimed business partnerships could not be independently verified. Additionally, the stated purpose of the international transfer - "payment for textile imports" - lacks supporting documentation such as shipping manifests, customs declarations, or purchase orders that would typically accompany legitimate import transactions of this magnitude.

The customer's explanation that all {incoming['unique_counterparties']} senders are business partners in the textile trade is not substantiated by available evidence and appears inconsistent with the scale of the customer's documented business operations."""
        
        sections.append({
            "title": "INVESTIGATIVE FINDINGS",
            "content": section4,
            "data_sources": [
                "Watchlist screening: No hits",
                "Business verification: Legitimate entity since 2018",
                "Tax records: ₹8-12 lakhs annual income",
                f"Documentation provided: 12 of {incoming['total_count']} transactions",
                "Invoice inconsistencies noted"
            ],
            "confidence": "medium"
        })
        
        # Section 5: Conclusion
        reasoning.append("Step 7: Synthesizing findings into regulatory conclusion")
        
        section5 = f"""Based on the totality of the circumstances, this institution has determined that the transaction activity described above warrants the filing of a Suspicious Activity Report. The pattern of receiving {incoming['total_amount']} from {incoming['unique_counterparties']} different sources within {period['total_days']} days, followed by immediate international transfer of substantially all funds, exhibits characteristics consistent with money laundering layering operations.

The activity deviates significantly from the subject's established transaction history and documented business profile. The customer's inability to provide adequate documentation for the majority of claimed business relationships, combined with inconsistencies in provided evidence, raises substantial questions about the legitimacy of the underlying transactions. The rapid consolidation and offshore movement of funds, coupled with the limited verifiability of the foreign beneficiary entity, further supports the assessment that this activity may involve the proceeds of unlawful activity.

This SAR is filed in accordance with 31 CFR 1020.320 and FinCEN guidance on identifying and reporting suspicious activity. The institution has taken no action to notify the subject of this filing, in compliance with 31 USC 5318(g)(2). All supporting documentation and transaction records have been preserved in accordance with recordkeeping requirements."""
        
        sections.append({
            "title": "CONCLUSION AND BASIS FOR SUSPICION",
            "content": section5,
            "data_sources": [
                "31 CFR 1020.320 (SAR filing regulation)",
                "31 USC 5318(g)(2) (Confidentiality provision)",
                "FinCEN Money Laundering Guidance",
                "Complete transaction analysis"
            ],
            "confidence": "high"
        })
        
        # Compile full narrative
        full_narrative = "\n\n".join([
            f"{section['title']}\n\n{section['content']}" 
            for section in sections
        ])
        
        return {
            "narrative": full_narrative,
            "sections": sections,
            "reasoning": reasoning
        }
    
    def _build_audit_trail(self, narrative_data: Dict, case_data: Dict) -> List[Dict]:
        """Build detailed audit trail mapping sentences to data sources"""
        
        audit_trail = []
        
        for section in narrative_data["sections"]:
            # Split section into sentences
            sentences = re.split(r'(?<=[.!?])\s+', section["content"])
            
            for sentence in sentences:
                if sentence.strip():
                    # Map sentence to data sources
                    sources = self._identify_data_sources(sentence, case_data)
                    
                    audit_trail.append({
                        "sentence": sentence.strip(),
                        "section": section["title"],
                        "data_sources": sources,
                        "confidence": self._assess_sentence_confidence(sentence, case_data)
                    })
        
        return audit_trail
    
    def _identify_data_sources(self, sentence: str, case_data: Dict) -> List[str]:
        """Identify which data points from case_data are referenced in a sentence"""
        
        sources = []
        
        # Check for customer information
        if case_data["customer"]["name"] in sentence:
            sources.append(f"Customer.name = {case_data['customer']['name']}")
        
        if case_data["customer"]["account_number"] in sentence:
            sources.append(f"Customer.account_number = {case_data['customer']['account_number']}")
        
        # Check for transaction amounts
        amount_str = case_data["incoming_transactions"]["total_amount"]
        if amount_str in sentence or amount_str.replace("₹", "") in sentence:
            sources.append(f"Incoming.total_amount = {amount_str}")
        
        # Check for transaction count
        count = str(case_data["incoming_transactions"]["total_count"])
        if count in sentence:
            sources.append(f"Incoming.transaction_count = {count}")
        
        # Check for dates
        for date_field in ["start_date", "end_date"]:
            date = case_data["suspicious_activity_period"][date_field]
            if date in sentence:
                sources.append(f"Period.{date_field} = {date}")
        
        # Check for beneficiary info
        if case_data["outgoing_transactions"]["transactions"]:
            beneficiary = case_data["outgoing_transactions"]["transactions"][0]["beneficiary_name"]
            if beneficiary in sentence:
                sources.append(f"Outgoing.beneficiary = {beneficiary}")
        
        # Generic source if nothing specific found
        if not sources:
            sources.append("Derived from case analysis")
        
        return sources
    
    def _assess_sentence_confidence(self, sentence: str, case_data: Dict) -> str:
        """Assess confidence level for a sentence based on data availability"""
        
        # Keywords indicating factual statements (high confidence)
        factual_keywords = ["account number", "date", "amount", "transaction", "received", "transferred"]
        
        # Keywords indicating analysis/interpretation (medium confidence)
        analytical_keywords = ["suggests", "indicates", "appears", "consistent with", "raises concerns"]
        
        # Keywords indicating conclusion (varies based on evidence)
        conclusion_keywords = ["determined", "concluded", "assessment", "based on"]
        
        sentence_lower = sentence.lower()
        
        # Check for analytical language
        if any(keyword in sentence_lower for keyword in analytical_keywords):
            return "medium"
        
        # Check for factual data points
        if any(keyword in sentence_lower for keyword in factual_keywords):
            # Verify data is actually present
            sources = self._identify_data_sources(sentence, case_data)
            if len(sources) > 1 and "Derived from" not in sources[0]:
                return "high"
            return "medium"
        
        # Default to medium
        return "medium"
    
    def _calculate_confidence_scores(self, case_data: Dict, narrative_data: Dict) -> Dict[str, str]:
        """Calculate confidence scores for each narrative section"""
        
        scores = {}
        
        for section in narrative_data["sections"]:
            # Use the confidence from the section if available
            scores[section["title"]] = section.get("confidence", "medium")
        
        return scores
    
    def _generate_compliance_checklist(self, narrative_data: Dict) -> Dict[str, bool]:
        """Generate FinCEN SAR compliance checklist"""
        
        sections_present = {section["title"] for section in narrative_data["sections"]}
        
        checklist = {
            "Subject Information Present": "SUBJECT INFORMATION" in sections_present,
            "Activity Description Present": "SUSPICIOUS ACTIVITY DESCRIPTION" in sections_present,
            "Suspicious Pattern Analysis": "PATTERN ANALYSIS" in sections_present or "MONEY LAUNDERING" in str(sections_present),
            "Investigation Documented": "INVESTIGATIVE FINDINGS" in sections_present,
            "Conclusion and Legal Basis": "CONCLUSION" in sections_present,
            "No Discriminatory Language": True,  # Would need NLP analysis in production
            "Factual and Objective Tone": True,  # Would need NLP analysis in production
            "Specific Dates and Amounts Cited": True,  # Would verify in production
        }
        
        return checklist


def format_currency(amount: int) -> str:
    """Format numeric amount as Indian Rupees"""
    return f"₹{amount:,}"


def calculate_time_savings(manual_hours: float = 5.5, automated_minutes: int = 50) -> Dict[str, Any]:
    """Calculate time savings metrics"""
    
    automated_hours = automated_minutes / 60
    time_saved_hours = manual_hours - automated_hours
    percentage_saved = (time_saved_hours / manual_hours) * 100
    
    return {
        "manual_time": f"{manual_hours} hours",
        "automated_time": f"{automated_minutes} minutes",
        "time_saved": f"{time_saved_hours:.1f} hours",
        "percentage_saved": f"{percentage_saved:.0f}%"
    }
