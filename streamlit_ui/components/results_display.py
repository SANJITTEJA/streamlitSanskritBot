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
        with st.expander("💡 AI Feedback", expanded=False):
            feedback = results['llm_feedback']
            st.markdown(f"""
                <div style="font-size: 0.9rem; color: #94a3b8; line-height: 1.5;">
                    {feedback.get('analysis', '')}<br/><br/>
                    <em style="color: #6366f1;">{feedback.get('motivation', '')}</em>
                </div>
            """, unsafe_allow_html=True)
