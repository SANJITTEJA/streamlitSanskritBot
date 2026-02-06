"""
Results Display Component
Compact analysis results with word practice selection
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
    
    # Compact incorrect words (if any) with selection option
    if results.get('incorrect_words'):
        with st.expander("🎯 Words to Practice", expanded=True):
            st.markdown("**Select words you'd like to practice individually:**")
            
            selected_words = []
            
            for i, word in enumerate(results['incorrect_words']):
                word_key = word.get('devanagari', word.get('original', ''))
                slp1 = word.get('slp1', word.get('original', ''))
                user_said = word.get('user', '')
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                        <div style="font-size: 0.9rem; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="color: #f1f5f9; font-weight: bold;">{word_key}</span><br/>
                            <span style="color: #94a3b8; font-size: 0.85rem;">
                                Expected: {slp1} | You said: {user_said}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.checkbox("✓", key=f"select_word_{i}", value=True, label_visibility="collapsed"):
                        selected_words.append(word)
            
            # Practice button
            if selected_words:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🎯 Practice Selected Words", type="primary", use_container_width=True):
                        st.session_state.words_to_practice = selected_words
                        st.session_state.current_word_practice_index = 0
                        st.session_state.practice_mode = 'word'
                        st.session_state.word_practice_result = None
                        st.rerun()
                
                with col2:
                    if st.button("🔤 Alphabet Practice", type="secondary", use_container_width=True):
                        st.session_state.practice_mode = 'alphabet'
                        st.rerun()
    
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

