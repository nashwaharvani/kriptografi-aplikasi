"""Tema visual EmberNote (CSS tambahan di atas .streamlit/config.toml)."""
import streamlit as st

CSS = """
<style>
.block-container { padding-top: 2rem; max-width: 820px; }
.en-hero { padding: 1.3rem 1.6rem; border-radius: 16px; margin-bottom: 1.2rem;
  background: linear-gradient(135deg, #FF6B35 0%, #C2410C 55%, #7C2D12 100%); color: #fff; }
.en-hero h1 { margin: 0; font-size: 2rem; color: #fff; padding: 0; }
.en-hero p { margin: .3rem 0 0; opacity: .92; }
.en-badge { display: inline-block; padding: .15rem .6rem; margin: .6rem .35rem 0 0; border-radius: 999px;
  font-size: .78rem; background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35); }
div[data-testid="stForm"] { border-radius: 14px; border: 1px solid rgba(255,107,53,.35); }
.stButton > button, div[data-testid="stFormSubmitButton"] > button { border-radius: 10px; font-weight: 600; }
</style>
"""


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, badges=()) -> None:
    chips = "".join(f'<span class="en-badge">{b}</span>' for b in badges)
    st.markdown(
        f'<div class="en-hero"><h1>{title}</h1><p>{subtitle}</p>{chips}</div>',
        unsafe_allow_html=True,
    )
