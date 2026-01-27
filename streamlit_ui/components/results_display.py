"""
Results Display Component
Compact analysis results
"""
import streamlit as st


def render_results_display():
    """Render compact analysis results"""
    results = st.session_state.analysis_results
    
    if not results:
        return
    
    accuracy = results['accuracy']
    passed = results['passed']
    
    # Compact result card
    bg_color = "rgba(16, 185, 129, 0.1)" if passed else "rgba(239, 68, 68, 0.1)"
    border_color = "#10b981" if passed else "#ef4444"
    icon = "✓" if passed else "📚"
    
    st.markdown(f"""
        <div style="background: {bg_color}; border-left: 3px solid {border_color}; 
             padding: 12px 16px; border-radius: 8px; margin: 8px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 1.3rem;">{icon}</span>
                    <span style="font-size: 1.1rem; font-weight: 600; color: #f1f5f9; margin-left: 8px;">
                        {accuracy}% Accuracy
                    </span>
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8;">
                    {results['correct_count']}/{results['total_count']} words
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Compact incorrect words (if any)
    if results.get('incorrect_words'):
        with st.expander("🎯 Words to Practice", expanded=False):
            for word in results['incorrect_words']:
                st.markdown(f"""
                    <div style="font-size: 0.9rem; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <span style="color: #f1f5f9; font-weight: bold;">{word.get('devanagari', word.get('original', ''))}</span><br/>
                        <span style="color: #94a3b8; font-size: 0.85rem;">
                            Expected: {word.get('slp1', word.get('original', ''))} | You said: {word.get('user', '')}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
    
    # Compact LLM feedback
    if results.get('llm_feedback'):
        with st.expander("💡 AI Feedback", expanded=True):
            feedback = results['llm_feedback']
            
            # Main feedback
            st.markdown(f"""
                <div style="font-size: 0.95rem; color: #e2e8f0; line-height: 1.6; margin-bottom: 12px;">
                    {feedback.get('analysis', '')}
                </div>
            """, unsafe_allow_html=True)
            
            # Motivation
            if feedback.get('motivation'):
                st.markdown(f"""
                    <div style="font-size: 0.9rem; color: #a78bfa; font-style: italic; margin-bottom: 12px;">
                        💜 {feedback.get('motivation', '')}
                    </div>
                """, unsafe_allow_html=True)
            
            # Practice tips
            if feedback.get('practice_tips'):
                st.markdown("""
                    <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 8px;">
                        <strong>Practice Tips:</strong>
                    </div>
                """, unsafe_allow_html=True)
                for tip in feedback.get('practice_tips', []):
                    st.markdown(f"""
                        <div style="font-size: 0.85rem; color: #94a3b8; padding-left: 12px;">
                            • {tip}
                        </div>
                    """, unsafe_allow_html=True)
