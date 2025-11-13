import streamlit as st
from docxtpl import DocxTemplate
from jinja2 import FileSystemLoader
import pickle
import io
import os
from datetime import date
import warnings
import docx
from docxcompose.composer import Composer
from docx import Document as DocxDocument 
# from automated_visuals import generate_all_visuals 

st.set_page_config(page_title="Psych Report Generator", layout="wide")
st.title("🧠 Psych Report Generator")

@st.cache_resource
def load_all_pickle_files():
    try:
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        ROOT_DIR = os.getcwd()
        
    folder_path = os.path.join(ROOT_DIR, 'dictionaries')
    
    resources = {}
    try:
        pkl_files = [
            'standard_score.pkl', 'scaled_score.pkl', 't_score.pkl',
            'vci_sum_dict.pkl', 'vsi_sum_dict.pkl', 'fri_sum_dict.pkl',
            'wmi_sum_dict.pkl', 'psi_sum_dict.pkl', 'fsiq_sum_dict.pkl',
            'tvps4_sum_standard_conversion.pkl', 'taps4_pp_am_sum_standard_conversion.pkl',
            'taps4_lc_sum_standard_conversion.pkl', 'taps4_overall_sum_standard_conversion.pkl',
            'ctopp2_sum_3_score.pkl', 'ctopp2_sum_2_score.pkl', 'wnv_dict.pkl',
            'ctoni_pictorial_scale_sum_dict.pkl', 'ctoni_geometric_scale_sum_dict.pkl',
            'ctoni_full_scale_sum_dict.pkl', 'cas_planning_dict.pkl',
            'cas_simultaneous_dict.pkl', 'cas_attention_dict.pkl', 'cas_successive_dict.pkl',
            'cas_fsiq_dict.pkl', 'cas_efwwm_dict.pkl', 'cas_efwowm_dict.pkl',
            'cas_wm_dict.pkl', 'cas_vc_dict.pkl', 'cas_nvc_dict.pkl',
            'sequential_gsm_dict_age4.pkl', 'simultaneous_gv_dict_age4.pkl',
            'learning_glr_dict_age4.pkl', 'knowledge_gc_dict_age4.pkl',
            'mpi_dict_age4.pkl', 'fci_dict_age4.pkl', 'nvi_dict_age4.pkl',
            'sequential_gsm_dict_age5.pkl', 'simultaneous_gv_dict_age5.pkl',
            'learning_glr_dict_age5.pkl', 'knowledge_gc_dict_age5.pkl',
            'mpi_dict_age5.pkl', 'fci_dict_age5.pkl', 'nvi_dict_age5.pkl',
            'sequential_gsm_dict_age6.pkl', 'simultaneous_gv_dict_age6.pkl',
            'learning_glr_dict_age6.pkl', 'knowledge_gc_dict_age6.pkl',
            'mpi_dict_age6.pkl', 'fci_dict_age6.pkl', 'nvi_dict_age6.pkl',
            'wraml_ac_dict.pkl', 'wraml_gmi_dict.pkl',
            'wraml_verbalim_dict.pkl', 'wraml_visualim_dict.pkl'
        ]

        for pkl_name in pkl_files:
            full_pkl_path = os.path.join(folder_path, pkl_name)
            with open(full_pkl_path, 'rb') as f:
                key_name = pkl_name.replace('.pkl', '')
                resources[key_name] = pickle.load(f)
        
        # Store the root path for later
        resources['root_dir'] = ROOT_DIR
        return resources

    except Exception as e:
        st.error(f"CRITICAL FILE ERROR: The app failed to load resources. Check file paths. Error: {e}")
        st.stop()

RES = load_all_pickle_files()

def calculate_age_as_numbers(dob, today):
    years = today.year - dob.year
    months = today.month - dob.month
    if today.day < dob.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return years, months

def get_standard_sl_p(standard_score_dict, key):
    if key in standard_score_dict:
        pct_standard_percentile = standard_score_dict[key][0]
        pct_standard_skill_level = standard_score_dict[key][1]
        return pct_standard_percentile, pct_standard_skill_level
    else:
        return None
    
def get_p_from_standard(standard_score_dict, key):
    if key in standard_score_dict:
        sl = standard_score_dict[key][0]
        return sl
    else:
        return None
    
def get_sl_from_standard(standard_score_dict, key):
    if key in standard_score_dict:
        sl = standard_score_dict[key][1]
        return sl
    else:
        return None

def get_sl_from_scaled(scaled_score_dict, key):
    if key in scaled_score_dict:
        sl = scaled_score_dict[key][1]
        return sl
    else:
        return None    

def get_p_from_scaled(scaled_score_dict, key):
    if key in scaled_score_dict:
        percentile_rank = scaled_score_dict[key][0]
        return percentile_rank
    else:
        return None

def get_p_from_tscore(t_score_dict, key):
    if key in t_score_dict:
        percentile_rank = t_score_dict[key][0]
        return percentile_rank
    else:
        return None

def get_sl_from_tscore(t_score_dict, key):
    if key in t_score_dict:
        sl = t_score_dict[key][1]
        return sl
    else:
        return None    
    
def student_pronouns(sex):
    if sex == 'male':
        return 'His', 'his', 'He', 'he', 'him'
    elif sex == 'female':
        return 'Her', 'her', 'She', 'she', 'her'
    else:
        return 'Their', 'their', 'They', 'they', 'them'

def get_ordinal_suffix_percentile(percentile):
    if percentile == '<0.1': return ""
    if percentile is None or percentile == "": return ""
    try:
        num = float(percentile)
    except (ValueError, TypeError): return ""
    if num < 1: return ""
    integer_part = int(num)
    if 11 <= (integer_part % 100) <= 13: return 'th'
    last_digit = integer_part % 10
    if last_digit == 1: return 'st'
    elif last_digit == 2: return 'nd'
    elif last_digit == 3: return 'rd'
    else: return 'th'

def get_wisc_percentile_sl(subtest_sum_dict, standard_score_dict, key):
    if key in subtest_sum_dict:
        composite_score = subtest_sum_dict[key][0]
        if composite_score in standard_score_dict:
            return standard_score_dict[composite_score][1]
    return ""    

def get_wisc_range_sl(subtest_sum_dict, standard_score_dict, key):
    if key in subtest_sum_dict:
        lower = subtest_sum_dict[key][6]
        higher = subtest_sum_dict[key][7]
        if lower in standard_score_dict and higher in standard_score_dict:
            lower_range = standard_score_dict[lower][1]
            higher_range = standard_score_dict[higher][1]
            if lower_range != higher_range:
                return f'{lower_range} to {higher_range} range'
            else:
                return f'{lower_range} range'
    return ""    

def get_taps_phrase(skill_level, context_key):
    if context_key == 'overall_concerns':
        if skill_level == "Very High": return "is indicative of exceptionally high skill in"
        elif skill_level == "High": return "is indicative of well-developed skill in"
        elif skill_level == "Above Average": return "is indicative of above-average skill in"
        elif skill_level == "High Average": return "is indicative of solid skill in"
        elif skill_level == "Average": return "suggests no concerns with"
        elif skill_level == "Low Average": return "may suggest some weakness in"
        elif skill_level == "Below Average": return "suggests notable weakness in"
        elif skill_level == "Low": return "suggests significant weakness in"
        elif skill_level == "Very Low": return "suggests a profound weakness in"
        else: return "ERROR!"
    elif context_key == 'performance_verb':
        if skill_level == "Very High": return "performed exceptionally well"
        elif skill_level == "High": return "performed skillfully"
        elif skill_level == "Above Average": return "performed proficiently"
        elif skill_level == "High Average": return "performed well"
        elif skill_level == "Average": return "performed adequately"
        elif skill_level == "Low Average": return "had some difficulty"
        elif skill_level == "Below Average": return "struggled"
        elif skill_level == "Low": return "struggled significantly"
        elif skill_level == "Very Low": return "was highly challenged by this task"
        else: return "ERROR!"
    elif context_key == 'conclusion':
        if skill_level == "Very High": return "indicating exceptional"
        elif skill_level == "High": return "indicating well-developed"
        elif skill_level == "Above Average": return "indicating above-average"
        elif skill_level == "High Average": return "indicating solid"
        elif skill_level == "Average": return "indicating appropriately developed"
        elif skill_level == "Low Average": return "indicating developing"
        elif skill_level == "Below Average": return "indicating underdeveloped"
        elif skill_level == "Low": return "indicating a significant weakness in"
        elif skill_level == "Very Low": return "indicating a profound weakness in"
        else: return "ERROR!"

def create_subtest_inputs(subtests_list, num_cols):
    """
    Creates number inputs for a list of subtests, but renders them
    column-by-column to ensure a vertical tab order.
    """
    inputs = {}
    items_per_col = (len(subtests_list) + num_cols - 1) // num_cols
    chunks = [subtests_list[i:i + items_per_col] for i in range(0, len(subtests_list), items_per_col)]
    
    columns = st.columns(num_cols)

    for col_index, chunk in enumerate(chunks):
        with columns[col_index]:
            for test in chunk:
                inputs[test['name']] = st.number_input(
                    test['display_name'], 
                    min_value=0, 
                    value=test.get('score', 0),
                    key=test['name']
                )
    return inputs

st.sidebar.header("Student Information")
st_name = st.sidebar.text_input("Student Name", value="")
st_sex = st.sidebar.selectbox("Student Sex", ["male", "female"], index=0)
st_dob = st.sidebar.date_input("Date of Birth", value=None, min_value=date(2000, 1, 1))
st_dot = st.sidebar.date_input("Date of Testing", value=date.today(), max_value=date.today())

if st_dob:
    age_years, age_months = calculate_age_as_numbers(st_dob, st_dot)
    st.sidebar.info(f"Calculated Age: {age_years} years, {age_months} months")
else:
    age_years, age_months = None, None 
    st.sidebar.warning("Please select a Date of Birth.")


tab_wisc, tab_ctoni, tab_wj, tab_tvps, tab_taps, tab_vmi, tab_ctopp, tab_cas, tab_wraml, tab_kabc, tab_wnv = st.tabs([
    "WISC-V", "CTONI-2", "WJ IV", "TVPS-4", "TAPS-4", "Beery VMI", "CTOPP-2", "CAS2", "WRAML3", "KABC-II", "WNV"
])

original_context = {
    'wisc_subtests': [{'display_name': 'Block Design', 'name': 'wisc_bd', 'score': 0}, ...], # This is just a placeholder for the logic
    # ... all other subtest lists
}

with tab_wisc:
    st.subheader("WISC-V Subtest Scaled Scores")
    wisc_inputs = create_subtest_inputs([
        {'display_name': 'Block Design', 'name': 'wisc_bd', 'score': 0},
        {'display_name': 'Similarities', 'name': 'wisc_similarities', 'score': 0},
        {'display_name': 'Matrix Reasoning', 'name': 'wisc_mr', 'score': 0},
        {'display_name': 'Digit Span', 'name': 'wisc_ds', 'score': 0},
        {'display_name': 'Coding', 'name': 'wisc_coding', 'score': 0},
        {'display_name': 'Vocabulary', 'name': 'wisc_vocab', 'score': 0},
        {'display_name': 'Figure Weights', 'name': 'wisc_fw', 'score': 0},
        {'display_name': 'Visual Puzzles', 'name': 'wisc_vp', 'score': 0},
        {'display_name': 'Picture Span', 'name': 'wisc_ps', 'score': 0},
        {'display_name': 'Symbol Search', 'name': 'wisc_ss', 'score': 0}
    ], num_cols=3)

with tab_ctoni:
    st.subheader("CTONI-2 Subtest Scores")
    ctoni_inputs = create_subtest_inputs([
        {'display_name': 'Pictorial Analogies', 'name': 'conti_pa', 'score': 0},
        {'display_name': 'Pictorial Categories', 'name': 'conti_pc', 'score': 0},
        {'display_name': 'Pictorial Sequences', 'name': 'conti_pseq', 'score': 0},
        {'display_name': 'Geometric Analogies', 'name': 'conti_ga', 'score': 0},
        {'display_name': 'Geometric Categories', 'name': 'conti_gc', 'score': 0},
        {'display_name': 'Geometric Sequences', 'name': 'conti_gseq', 'score': 0}
    ], num_cols=2)

with tab_wj:
    st.subheader("WJ IV Subtest/Index Standard Scores")
    wj_inputs = create_subtest_inputs([
        {'display_name': 'Broad Reading', 'name': 'wj_br', 'score': 0},
        {'display_name': 'Basic Reading Skills', 'name': 'wj_brs', 'score': 0},
        {'display_name': 'Reading Comprehension', 'name': 'wj_rc', 'score': 0},
        {'display_name': 'Reading Fluency', 'name': 'wj_rf', 'score': 0},
        {'display_name': 'Letter-Word Identification', 'name': 'wj_lwi', 'score': 0},
        {'display_name': 'Passage Comprehension', 'name': 'wj_pc', 'score': 0},
        {'display_name': 'Sentence Reading Fluency', 'name': 'wj_srf', 'score': 0},
        {'display_name': 'Word Attack', 'name': 'wj_wa', 'score': 0},
        {'display_name': 'Reading Recall', 'name': 'wj_rr', 'score': 0},
        {'display_name': 'Oral Reading', 'name': 'wj_or', 'score': 0},
        {'display_name': 'Broad Mathematics', 'name': 'wj_bm', 'score': 0},
        {'display_name': 'Math Calculation Skills', 'name': 'wj_mcs', 'score': 0},
        {'display_name': 'Math Problem Solving', 'name': 'wj_mps', 'score': 0},
        {'display_name': 'Applied Problems', 'name': 'wj_ap', 'score': 0},
        {'display_name': 'Calculation', 'name': 'wj_c', 'score': 0},
        {'display_name': 'Math Facts Fluency', 'name': 'wj_mff', 'score': 0},
        {'display_name': 'Number Matrices', 'name': 'wj_nm', 'score': 0},
        {'display_name': 'Broad Written Language', 'name': 'wj_bwl', 'score': 0},
        {'display_name': 'Written Expression', 'name': 'wj_we', 'score': 0},
        {'display_name': 'Spelling', 'name': 'wj_s', 'score': 0},
        {'display_name': 'Writing Samples', 'name': 'wj_ws', 'score': 0},
        {'display_name': 'Sentence Writing Fluency', 'name': 'wj_swf', 'score': 0}
    ], num_cols=3)

with tab_tvps:
    st.subheader("TVPS-4 Subtest Scaled Scores")
    tvps4_inputs = create_subtest_inputs([
        {'display_name': 'Visual Discrimination', 'name': 'tvps4_vd', 'score': 0},
        {'display_name': 'Visual Memory', 'name': 'tvps4_vm', 'score': 0},
        {'display_name': 'Spatial Relationships', 'name': 'tvps4_sr', 'score': 0},
        {'display_name': 'Form Constancy', 'name': 'tvps4_fc', 'score': 0},
        {'display_name': 'Sequential Memory', 'name': 'tvps4_sm', 'score': 0},
        {'display_name': 'Figure-Ground', 'name': 'tvps4_fg', 'score': 0},
        {'display_name': 'Visual Closure', 'name': 'tvps4_vc', 'score': 0}
    ], num_cols=3)

with tab_taps:
    st.subheader("TAPS-4 Subtest Scaled Scores")
    taps4_inputs = create_subtest_inputs([
        {'display_name': 'Word Discrimination', 'name': 'taps4_wd', 'score': 0},
        {'display_name': 'Phonological Deletion', 'name': 'taps4_pd', 'score': 0},
        {'display_name': 'Phonological Blending', 'name': 'taps4_pb', 'score': 0},
        {'display_name': 'Number Memory Forward', 'name': 'taps4_nmf', 'score': 0},
        {'display_name': 'Word Memory', 'name': 'taps4_wm', 'score': 0},
        {'display_name': 'Sentence Memory', 'name': 'taps4_sm', 'score': 0},
        {'display_name': 'Processing Oral Directions', 'name': 'taps4_pod', 'score': 0},
        {'display_name': 'Auditory Comprehension', 'name': 'taps4_ac', 'score': 0}
    ], num_cols=3)

with tab_vmi:
    st.subheader("Beery VMI Standard Score")
    vmi_inputs = create_subtest_inputs([
        {'display_name': 'Visual-Motor Integration', 'name': 'vmi_standard_score', 'score': 0}
    ], num_cols=1)

with tab_ctopp:
    st.subheader("CTOPP-2 Subtest Scaled Scores")
    ctopp2_inputs = create_subtest_inputs([
        {'display_name': 'Elision', 'name': 'ctopp2_elision', 'score': 0},
        {'display_name': 'Blending Words', 'name': 'ctopp2_bw', 'score': 0},
        {'display_name': 'Phoneme Isolation', 'name': 'ctopp2_pi', 'score': 0},
        {'display_name': 'Sound Matching', 'name': 'ctopp2_sm', 'score': 0},
        {'display_name': 'Memory for Digits', 'name': 'ctopp2_md', 'score': 0},
        {'display_name': 'Nonword Repetition', 'name': 'ctopp2_nr', 'score': 0},
        {'display_name': 'Rapid Digit Naming', 'name': 'ctopp2_rdn', 'score': 0},
        {'display_name': 'Rapid Letter Naming', 'name': 'ctopp2_rln', 'score': 0},
        {'display_name': 'Rapid Color Naming', 'name': 'ctopp2_rcn', 'score': 0},
        {'display_name': 'Rapid Object Naming', 'name': 'ctopp2_ron', 'score': 0}
    ], num_cols=3)

with tab_cas:
    st.subheader("CAS2 Subtest Scaled Scores")
    cas_inputs = create_subtest_inputs([
        {'display_name': 'Planned Codes', 'name': 'cas_pcodes', 'score': 0},
        {'display_name': 'Planned Connections', 'name': 'cas_pcon', 'score': 0},
        {'display_name': 'Matrices', 'name': 'cas_matrices', 'score': 0},
        {'display_name': 'Verbal-Spatial Relations', 'name': 'cas_vsr', 'score': 0},
        {'display_name': 'Expressive Attention', 'name': 'cas_ea', 'score': 0},
        {'display_name': 'Number Detection', 'name': 'cas_nd', 'score': 0},
        {'display_name': 'Word Series', 'name': 'cas_ws', 'score': 0},
        {'display_name': 'Sentence Repetition/Questions', 'name': 'cas_srq', 'score': 0},
        {'display_name': 'Receptive Attention', 'name': 'cas_ra', 'score': 0},
        {'display_name': 'Figure Memory', 'name': 'cas_fm', 'score': 0}
    ], num_cols=3)

with tab_wraml:
    st.subheader("WRAML3 Subtest Scaled Scores")
    wraml_inputs = create_subtest_inputs([
        {'display_name': 'Picture Memory', 'name': 'wraml_pm', 'score': 0},
        {'display_name': 'Design Learning', 'name': 'wraml_dl', 'score': 0},
        {'display_name': 'Story Memory', 'name': 'wraml_sm', 'score': 0},
        {'display_name': 'Verbal Learning', 'name': 'wraml_vl', 'score': 0},
        {'display_name': 'Finger Windows', 'name': 'wraml_fw', 'score': 0},
        {'display_name': 'Number Letter', 'name': 'wraml_nl', 'score': 0}
    ], num_cols=2)

with tab_kabc:
    st.subheader("KABC-II NU Subtest Scaled Scores")
    kabc_inputs = create_subtest_inputs([
        {'display_name': 'Number Recall', 'name': 'kabc_nr', 'score': 0},
        {'display_name': 'Word Order', 'name': 'kabc_wo', 'score': 0},
        {'display_name': 'Atlantis', 'name': 'kabc_atlantis', 'score': 0},
        {'display_name': 'Rebus', 'name': 'kabc_rebus', 'score': 0},
        {'display_name': 'Rover', 'name': 'kabc_rover', 'score': 0},
        {'display_name': 'Triangles Block Counting', 'name': 'kabc_t', 'score': 0},
        {'display_name': 'Block Counting', 'name': 'kabc_bc', 'score': 0},
        {'display_name': 'Verbal Knowledge', 'name': 'kabc_vk', 'score': 0},
        {'display_name': 'Riddles', 'name': 'kabc_riddles', 'score': 0}
    ], num_cols=3)
    
    st.subheader("KABC-II NU Nonverbal Subtest Scaled Scores")
    kabc_nv_inputs = create_subtest_inputs([
        {'display_name': 'Story Completion', 'name': 'kabc_nv_sc', 'score': 0},
        {'display_name': 'Triangles', 'name': 'kabc_nv_triangles', 'score': 0},
        {'display_name': 'Block Counting', 'name': 'kabc_nv_bc', 'score': 0},
        {'display_name': 'Pattern Reasoning', 'name': 'kabc_nv_pr', 'score': 0},
        {'display_name': 'Hand Movements', 'name': 'kabc_nv_hm', 'score': 0}
    ], num_cols=2)

with tab_wnv:
    st.subheader("WNV Subtest T-Scores")
    wnv_inputs = create_subtest_inputs([
        {'display_name':'Matrix Reasoning', 'name': 'wnv_mr', 'score': 0},
        {'display_name':'Coding', 'name': 'wnv_coding', 'score': 0},
        {'display_name':'Recognition', 'name': 'wnv_recognition', 'score': 0},
        {'display_name':'Spatial Span', 'name': 'wnv_ss', 'score': 0},
        {'display_name':'Picture Arrangement', 'name': 'wnv_pa', 'score': 0},
        {'display_name':'Object Assembly', 'name': 'wnv_oa', 'score': 0}
    ], num_cols=2)

st.divider()
if st.button("GENERATE REPORT 📄", type="primary", use_container_width=True):
    context = {
        'name': st_name,
        'student_sex': st_sex,
        'dob': st_dob.isoformat() if st_dob else "",
        'date_of_testing': st_dot.isoformat(),
        'wisc_subtests': [{'display_name': 'Block Design', 'name': 'wisc_bd', 'score': wisc_inputs['wisc_bd']},
                          {'display_name': 'Similarities', 'name': 'wisc_similarities', 'score': wisc_inputs['wisc_similarities']},
                          {'display_name': 'Matrix Reasoning', 'name': 'wisc_mr', 'score': wisc_inputs['wisc_mr']},
                          {'display_name': 'Digit Span', 'name': 'wisc_ds', 'score': wisc_inputs['wisc_ds']},
                          {'display_name': 'Coding', 'name': 'wisc_coding', 'score': wisc_inputs['wisc_coding']},
                          {'display_name': 'Vocabulary', 'name': 'wisc_vocab', 'score': wisc_inputs['wisc_vocab']},
                          {'display_name': 'Figure Weights', 'name': 'wisc_fw', 'score': wisc_inputs['wisc_fw']},
                          {'display_name': 'Visual Puzzles', 'name': 'wisc_vp', 'score': wisc_inputs['wisc_vp']},
                          {'display_name': 'Picture Span', 'name': 'wisc_ps', 'score': wisc_inputs['wisc_ps']},
                          {'display_name': 'Symbol Search', 'name': 'wisc_ss', 'score': wisc_inputs['wisc_ss']}],
        'ctoni_subtests': [{'display_name': 'Pictorial Analogies', 'name': 'conti_pa', 'score': ctoni_inputs['conti_pa']},
                           {'display_name': 'Pictorial Categories', 'name': 'conti_pc', 'score': ctoni_inputs['conti_pc']},
                           {'display_name': 'Pictorial Sequences', 'name': 'conti_pseq', 'score': ctoni_inputs['conti_pseq']},
                           {'display_name': 'Geometric Analogies', 'name': 'conti_ga', 'score': ctoni_inputs['conti_ga']},
                           {'display_name': 'Geometric Categories', 'name': 'conti_gc', 'score': ctoni_inputs['conti_gc']},
                           {'display_name': 'Geometric Sequences', 'name': 'conti_gseq', 'score': ctoni_inputs['conti_gseq']}],
        'wj_subtests': [{'display_name': 'Broad Reading', 'name': 'wj_br', 'score': wj_inputs['wj_br']},
                        {'display_name': 'Basic Reading Skills', 'name': 'wj_brs', 'score': wj_inputs['wj_brs']},
                        {'display_name': 'Reading Comprehension', 'name': 'wj_rc', 'score': wj_inputs['wj_rc']},
                        {'display_name': 'Reading Fluency', 'name': 'wj_rf', 'score': wj_inputs['wj_rf']},
                        {'display_name': 'Letter-Word Identification', 'name': 'wj_lwi', 'score': wj_inputs['wj_lwi']},
                        {'display_name': 'Passage Comprehension', 'name': 'wj_pc', 'score': wj_inputs['wj_pc']},
                        {'display_name': 'Sentence Reading Fluency', 'name': 'wj_srf', 'score': wj_inputs['wj_srf']},
                        {'display_name': 'Word Attack', 'name': 'wj_wa', 'score': wj_inputs['wj_wa']},
                        {'display_name': 'Reading Recall', 'name': 'wj_rr', 'score': wj_inputs['wj_rr']},
                        {'display_name': 'Oral Reading', 'name': 'wj_or', 'score': wj_inputs['wj_or']},
                        {'display_name': 'Broad Mathematics', 'name': 'wj_bm', 'score': wj_inputs['wj_bm']},
                        {'display_name': 'Math Calculation Skills', 'name': 'wj_mcs', 'score': wj_inputs['wj_mcs']},
                        {'display_name': 'Math Problem Solving', 'name': 'wj_mps', 'score': wj_inputs['wj_mps']},
                        {'display_name': 'Applied Problems', 'name': 'wj_ap', 'score': wj_inputs['wj_ap']},
                        {'display_name': 'Calculation', 'name': 'wj_c', 'score': wj_inputs['wj_c']},
                        {'display_name': 'Math Facts Fluency', 'name': 'wj_mff', 'score': wj_inputs['wj_mff']},
                        {'display_name': 'Number Matrices', 'name': 'wj_nm', 'score': wj_inputs['wj_nm']},
                        {'display_name': 'Broad Written Language', 'name': 'wj_bwl', 'score': wj_inputs['wj_bwl']},
                        {'display_name': 'Written Expression', 'name': 'wj_we', 'score': wj_inputs['wj_we']},
                        {'display_name': 'Spelling', 'name': 'wj_s', 'score': wj_inputs['wj_s']},
                        {'display_name': 'Writing Samples', 'name': 'wj_ws', 'score': wj_inputs['wj_ws']},
                        {'display_name': 'Sentence Writing Fluency', 'name': 'wj_swf', 'score': wj_inputs['wj_swf']}],
        'tvps4_subtests': [{'display_name': 'Visual Discrimination', 'name': 'tvps4_vd', 'score': tvps4_inputs['tvps4_vd']},
                           {'display_name': 'Visual Memory', 'name': 'tvps4_vm', 'score': tvps4_inputs['tvps4_vm']},
                           {'display_name': 'Spatial Relationships', 'name': 'tvps4_sr', 'score': tvps4_inputs['tvps4_sr']},
                           {'display_name': 'Form Constancy', 'name': 'tvps4_fc', 'score': tvps4_inputs['tvps4_fc']},
                           {'display_name': 'Sequential Memory', 'name': 'tvps4_sm', 'score': tvps4_inputs['tvps4_sm']},
                           {'display_name': 'Figure-Ground', 'name': 'tvps4_fg', 'score': tvps4_inputs['tvps4_fg']},
                           {'display_name': 'Visual Closure', 'name': 'tvps4_vc', 'score': tvps4_inputs['tvps4_vc']}],
        'taps4_subtests': [{'display_name': 'Word Discrimination', 'name': 'taps4_wd', 'score': taps4_inputs['taps4_wd']},
                           {'display_name': 'Phonological Deletion', 'name': 'taps4_pd', 'score': taps4_inputs['taps4_pd']},
                           {'display_name': 'Phonological Blending', 'name': 'taps4_pb', 'score': taps4_inputs['taps4_pb']},
                           {'display_name': 'Number Memory Forward', 'name': 'taps4_nmf', 'score': taps4_inputs['taps4_nmf']},
                           {'display_name': 'Word Memory', 'name': 'taps4_wm', 'score': taps4_inputs['taps4_wm']},
                           {'display_name': 'Sentence Memory', 'name': 'taps4_sm', 'score': taps4_inputs['taps4_sm']},
                           {'display_name': 'Processing Oral Directions', 'name': 'taps4_pod', 'score': taps4_inputs['taps4_pod']},
                           {'display_name': 'Auditory Comprehension', 'name': 'taps4_ac', 'score': taps4_inputs['taps4_ac']}],
        'vmi_scores': [{'display_name': 'Visual-Motor Integration', 'name': 'vmi_standard_score', 'score': vmi_inputs['vmi_standard_score']}],
        'ctopp2_subtests': [{'display_name': 'Elision', 'name': 'ctopp2_elision', 'score': ctopp2_inputs['ctopp2_elision']},
                            {'display_name': 'Blending Words', 'name': 'ctopp2_bw', 'score': ctopp2_inputs['ctopp2_bw']},
                            {'display_name': 'Phoneme Isolation', 'name': 'ctopp2_pi', 'score': ctopp2_inputs['ctopp2_pi']},
                            {'display_name': 'Sound Matching', 'name': 'ctopp2_sm', 'score': ctopp2_inputs['ctopp2_sm']},
                            {'display_name': 'Memory for Digits', 'name': 'ctopp2_md', 'score': ctopp2_inputs['ctopp2_md']},
                            {'display_name': 'Nonword Repetition', 'name': 'ctopp2_nr', 'score': ctopp2_inputs['ctopp2_nr']},
                            {'display_name': 'Rapid Digit Naming', 'name': 'ctopp2_rdn', 'score': ctopp2_inputs['ctopp2_rdn']},
                            {'display_name': 'Rapid Letter Naming', 'name': 'ctopp2_rln', 'score': ctopp2_inputs['ctopp2_rln']},
                            {'display_name': 'Rapid Color Naming', 'name': 'ctopp2_rcn', 'score': ctopp2_inputs['ctopp2_rcn']},
                            {'display_name': 'Rapid Object Naming', 'name': 'ctopp2_ron', 'score': ctopp2_inputs['ctopp2_ron']}],
        'cas_subtests': [{'display_name': 'Planned Codes', 'name': 'cas_pcodes', 'score': cas_inputs['cas_pcodes']},
                         {'display_name': 'Planned Connections', 'name': 'cas_pcon', 'score': cas_inputs['cas_pcon']},
                         {'display_name': 'Matrices', 'name': 'cas_matrices', 'score': cas_inputs['cas_matrices']},
                         {'display_name': 'Verbal-Spatial Relations', 'name': 'cas_vsr', 'score': cas_inputs['cas_vsr']},
                         {'display_name': 'Expressive Attention', 'name': 'cas_ea', 'score': cas_inputs['cas_ea']},
                         {'display_name': 'Number Detection', 'name': 'cas_nd', 'score': cas_inputs['cas_nd']},
                         {'display_name': 'Word Series', 'name': 'cas_ws', 'score': cas_inputs['cas_ws']},
                         {'display_name': 'Sentence Repetition/Questions', 'name': 'cas_srq', 'score': cas_inputs['cas_srq']},
                         {'display_name': 'Receptive Attention', 'name': 'cas_ra', 'score': cas_inputs['cas_ra']},
                         {'display_name': 'Figure Memory', 'name': 'cas_fm', 'score': cas_inputs['cas_fm']}],
        'wraml_subtests': [{'display_name': 'Picture Memory', 'name': 'wraml_pm', 'score': wraml_inputs['wraml_pm']},
                           {'display_name': 'Design Learning', 'name': 'wraml_dl', 'score': wraml_inputs['wraml_dl']},
                           {'display_name': 'Story Memory', 'name': 'wraml_sm', 'score': wraml_inputs['wraml_sm']},
                           {'display_name': 'Verbal Learning', 'name': 'wraml_vl', 'score': wraml_inputs['wraml_vl']},
                           {'display_name': 'Finger Windows', 'name': 'wraml_fw', 'score': wraml_inputs['wraml_fw']},
                           {'display_name': 'Number Letter', 'name': 'wraml_nl', 'score': wraml_inputs['wraml_nl']}],
        'kabc_subtests': [{'display_name': 'Number Recall', 'name': 'kabc_nr', 'score': kabc_inputs['kabc_nr']},
                          {'display_name': 'Word Order', 'name': 'kabc_wo', 'score': kabc_inputs['kabc_wo']},
                          {'display_name': 'Atlantis', 'name': 'kabc_atlantis', 'score': kabc_inputs['kabc_atlantis']},
                          {'display_name': 'Rebus', 'name': 'kabc_rebus', 'score': kabc_inputs['kabc_rebus']},
                          {'display_name': 'Rover', 'name': 'kabc_rover', 'score': kabc_inputs['kabc_rover']},
                          {'display_name': 'Triangles Block Counting', 'name': 'kabc_t', 'score': kabc_inputs['kabc_t']},
                          {'display_name': 'Block Counting', 'name': 'kabc_bc', 'score': kabc_inputs['kabc_bc']},
                          {'display_name': 'Verbal Knowledge', 'name': 'kabc_vk', 'score': kabc_inputs['kabc_vk']},
                          {'display_name': 'Riddles', 'name': 'kabc_riddles', 'score': kabc_inputs['kabc_riddles']}],
        'kabc_nv_subtests': [{'display_name': 'Story Completion', 'name': 'kabc_nv_sc', 'score': kabc_nv_inputs['kabc_nv_sc']},
                             {'display_name': 'Triangles', 'name': 'kabc_nv_triangles', 'score': kabc_nv_inputs['kabc_nv_triangles']},
                             {'display_name': 'Block Counting', 'name': 'kabc_nv_bc', 'score': kabc_nv_inputs['kabc_nv_bc']},
                             {'display_name': 'Pattern Reasoning', 'name': 'kabc_nv_pr', 'score': kabc_nv_inputs['kabc_nv_pr']},
                             {'display_name': 'Hand Movements', 'name': 'kabc_nv_hm', 'score': kabc_nv_inputs['kabc_nv_hm']}],
        'wnv_subtests': [{'display_name':'Matrix Reasoning', 'name': 'wnv_mr', 'score': wnv_inputs['wnv_mr']},
                         {'display_name':'Coding', 'name': 'wnv_coding', 'score': wnv_inputs['wnv_coding']},
                         {'display_name':'Recognition', 'name': 'wnv_recognition', 'score': wnv_inputs['wnv_recognition']},
                         {'display_name':'Spatial Span', 'name': 'wnv_ss', 'score': wnv_inputs['wnv_ss']},
                         {'display_name':'Picture Arrangement', 'name': 'wnv_pa', 'score': wnv_inputs['wnv_pa']},
                         {'display_name':'Object Assembly', 'name': 'wnv_oa', 'score': wnv_inputs['wnv_oa']}]
    }

    dob_str = context.get('dob')
    testing_date_str = context.get('date_of_testing')
    age_years, age_months = None, None

    if dob_str:
        dob = date.fromisoformat(dob_str)
        if testing_date_str:
            evaluation_date = date.fromisoformat(testing_date_str)
        else:
            evaluation_date = date.today()
        age_years, age_months = calculate_age_as_numbers(dob, evaluation_date)

    context['student_age_years'] = age_years
    context['student_age_months'] = age_months

    context['student_upper_pos_pronoun'], context['student_lower_pos_pronoun'], context['student_upper_per_pronoun'], context['student_lower_per_pronoun'], context['student_lower_obj_pronoun'] = student_pronouns(context['student_sex'])

    for item in context['vmi_scores']:
        context[item['name']] = item['score']
    vmi_has_scores = any(item['score'] for item in context['vmi_scores'])
    context['vmi_has_scores'] = vmi_has_scores
    vmi_score = context.get('vmi_standard_score')

    if vmi_score:
        scores = get_standard_sl_p(RES['standard_score'], vmi_score)
        percentile, skill_level = scores if scores else ("", "")
        context.update({
            'vmi_standard_percentile': percentile,
            'vmi_standard_sl': skill_level
        })
    else:
        context.update({
            'vmi_standard_percentile': "",
            'vmi_standard_sl': ""
        })
    student_skill_level = context.get('vmi_standard_sl') # Reads from correct key
    simple_key = 'vmi_simple_descriptor'
    if student_skill_level in ["Low Average", "Average", "High Average", "Above Average", "High", "Very High"]:
        simple_descriptor = "is able"
    else:
        simple_descriptor = "struggles"
    context[simple_key] = simple_descriptor
    complex_key = 'vmi_complex_descriptor'
    if student_skill_level in ["High", "Very High"]:
        complex_descriptor = "demonstrates strong proficiency in"
    elif student_skill_level in ["High Average", "Above Average"]:
        complex_descriptor = "is skilled at"
    elif student_skill_level == "Average":
        complex_descriptor = "is generally capable of"
    elif student_skill_level in ["Low Average", "Below Average"]:
        complex_descriptor = "has some difficulty with"
    elif student_skill_level in ["Low", "Very Low"]:
        complex_descriptor = "consistently struggles with"
    else:
        complex_descriptor = "has some difficulty with"
    context[complex_key] = complex_descriptor

    for subtest in context['wisc_subtests']:
        context[subtest['name']] = subtest['score']
    wisc_has_scores = any(test['score'] for test in context['wisc_subtests'])
    context['wisc_has_scores'] = wisc_has_scores
    wisc_scores_lookup = {item['name']: item['score'] for item in context['wisc_subtests']}
    vci_sum = (wisc_scores_lookup.get('wisc_similarities', 0) or 0) + (wisc_scores_lookup.get('wisc_vocab', 0) or 0)
    vsi_sum = (wisc_scores_lookup.get('wisc_bd', 0) or 0) + (wisc_scores_lookup.get('wisc_vp', 0) or 0)
    fri_sum = (wisc_scores_lookup.get('wisc_mr', 0) or 0) + (wisc_scores_lookup.get('wisc_fw', 0) or 0)
    wmi_sum = (wisc_scores_lookup.get('wisc_ds', 0) or 0) + (wisc_scores_lookup.get('wisc_ps', 0) or 0)
    psi_sum = (wisc_scores_lookup.get('wisc_coding', 0) or 0) + (wisc_scores_lookup.get('wisc_ss', 0) or 0)
    fsiq_sum = (wisc_scores_lookup.get('wisc_bd', 0) or 0) + \
             (wisc_scores_lookup.get('wisc_similarities', 0) or 0) + \
             (wisc_scores_lookup.get('wisc_mr', 0) or 0) + \
             (wisc_scores_lookup.get('wisc_ds', 0) or 0) + \
             (wisc_scores_lookup.get('wisc_coding', 0) or 0) + \
             (wisc_scores_lookup.get('wisc_vocab', 0) or 0) + \
             (wisc_scores_lookup.get('wisc_fw', 0) or 0)

    if vci_sum and vci_sum in RES['vci_sum_dict']:
        data = RES['vci_sum_dict'][vci_sum]
        vci_percentile = data[1] 
        context.update({
            'vci_sum': vci_sum, 'vci_ss': data[0], 'vci_percentile': vci_percentile,
            'vci_95_ci_range': data[5],
            'vci_percentile_sl': get_wisc_percentile_sl(RES['vci_sum_dict'], RES['standard_score'], vci_sum),
            'vci_95_ci_sl': get_wisc_range_sl(RES['vci_sum_dict'], RES['standard_score'], vci_sum),
            'vci_ordinal_suffix': get_ordinal_suffix_percentile(vci_percentile),
        })
    else:
        context.update({
            'vci_sum': "", 'vci_ss': "", 'vci_percentile': "", 'vci_95_ci_range': "",
            'vci_percentile_sl': "", 'vci_95_ci_sl': "", 'vci_ordinal_suffix': "",
        })
    if vsi_sum and vsi_sum in RES['vsi_sum_dict']:
        data = RES['vsi_sum_dict'][vsi_sum]
        vsi_percentile = data[1]
        context.update({
            'vsi_sum': vsi_sum, 'vsi_ss': data[0], 'vsi_percentile': vsi_percentile,
            'vsi_95_ci_range': data[5],
            'vsi_percentile_sl': get_wisc_percentile_sl(RES['vsi_sum_dict'], RES['standard_score'], vsi_sum),
            'vsi_95_ci_sl': get_wisc_range_sl(RES['vsi_sum_dict'], RES['standard_score'], vsi_sum),
            'vsi_ordinal_suffix': get_ordinal_suffix_percentile(vsi_percentile),
        })
    else:
        context.update({
            'vsi_sum': "", 'vsi_ss': "", 'vsi_percentile': "", 'vsi_95_ci_range': "",
            'vsi_percentile_sl': "", 'vsi_95_ci_sl': "", 'vsi_ordinal_suffix': "",
        })
    if fri_sum and fri_sum in RES['fri_sum_dict']:
        data = RES['fri_sum_dict'][fri_sum]
        fri_percentile = data[1]
        context.update({
            'fri_sum': fri_sum, 'fri_ss': data[0], 'fri_percentile': fri_percentile,
            'fri_95_ci_range': data[5],
            'fri_percentile_sl': get_wisc_percentile_sl(RES['fri_sum_dict'], RES['standard_score'], fri_sum),
            'fri_95_ci_sl': get_wisc_range_sl(RES['fri_sum_dict'], RES['standard_score'], fri_sum),
            'fri_ordinal_suffix': get_ordinal_suffix_percentile(fri_percentile),
        })
    else:
        context.update({
            'fri_sum': "", 'fri_ss': "", 'fri_percentile': "", 'fri_95_ci_range': "",
            'fri_percentile_sl': "", 'fri_95_ci_sl': "", 'fri_ordinal_suffix': "",
        })
    if wmi_sum and wmi_sum in RES['wmi_sum_dict']:
        data = RES['wmi_sum_dict'][wmi_sum]
        wmi_percentile = data[1]
        context.update({
            'wmi_sum': wmi_sum, 'wmi_ss': data[0], 'wmi_percentile': wmi_percentile,
            'wmi_95_ci_range': data[5],
            'wmi_percentile_sl': get_wisc_percentile_sl(RES['wmi_sum_dict'], RES['standard_score'], wmi_sum),
            'wmi_95_ci_sl': get_wisc_range_sl(RES['wmi_sum_dict'], RES['standard_score'], wmi_sum),
            'wmi_ordinal_suffix': get_ordinal_suffix_percentile(wmi_percentile),
        })
    else:
        context.update({
            'wmi_sum': "", 'wmi_ss': "", 'wmi_percentile': "", 'wmi_95_ci_range': "",
            'wmi_percentile_sl': "", 'wmi_95_ci_sl': "", 'wmi_ordinal_suffix': "",
        })
    if psi_sum and psi_sum in RES['psi_sum_dict']:
        data = RES['psi_sum_dict'][psi_sum]
        psi_percentile = data[1]
        context.update({
            'psi_sum': psi_sum, 'psi_ss': data[0], 'psi_percentile': psi_percentile,
            'psi_95_ci_range': data[5],
            'psi_percentile_sl': get_wisc_percentile_sl(RES['psi_sum_dict'], RES['standard_score'], psi_sum),
            'psi_95_ci_sl': get_wisc_range_sl(RES['psi_sum_dict'], RES['standard_score'], psi_sum),
            'psi_ordinal_suffix': get_ordinal_suffix_percentile(psi_percentile),
        })
    else:
        context.update({
            'psi_sum': "", 'psi_ss': "", 'psi_percentile': "", 'psi_95_ci_range': "",
            'psi_percentile_sl': "", 'psi_95_ci_sl': "", 'psi_ordinal_suffix': "",
        })
    if fsiq_sum and fsiq_sum in RES['fsiq_sum_dict']:
        data = RES['fsiq_sum_dict'][fsiq_sum]
        fsiq_percentile = data[1]
        context.update({
            'fsiq_sum': fsiq_sum, 'fsiq_ss': data[0], 'fsiq_percentile': fsiq_percentile,
            'fsiq_95_ci_range': data[5],
            'fsiq_percentile_sl': get_wisc_percentile_sl(RES['fsiq_sum_dict'], RES['standard_score'], fsiq_sum),
            'fsiq_95_ci_sl': get_wisc_range_sl(RES['fsiq_sum_dict'], RES['standard_score'], fsiq_sum),
            'fsiq_ordinal_suffix': get_ordinal_suffix_percentile(fsiq_percentile),
        })
    else:
        context.update({
            'fsiq_sum': "", 'fsiq_ss': "", 'fsiq_percentile': "", 'fsiq_95_ci_range': "",
            'fsiq_percentile_sl': "", 'fsiq_95_ci_sl': "", 'fsiq_ordinal_suffix': "",
        })
    for subtest in context['wisc_subtests']:
        subtest_name = subtest['name']
        subtest_score = subtest['score']
        base_name = subtest_name.split('_', 1)[1] if '_' in subtest_name else subtest_name
        sl_key = f"{base_name}_sl"
        if subtest_score:
            skill_level = get_sl_from_scaled(RES['scaled_score'], subtest_score)
            context[sl_key] = skill_level if skill_level else ""
        else:
            context[sl_key] = ""

    for subtest in context['ctoni_subtests']:
        context[subtest['name']] = subtest['score']
    ctoni_has_scores = any(test['score'] for test in context['ctoni_subtests'])
    context['ctoni_has_scores'] = ctoni_has_scores
    ctoni_scores_lookup = {item['name']: item['score'] for item in context['ctoni_subtests']}
    ctoni_ps_sum = (ctoni_scores_lookup.get('conti_pa', 0) or 0) + (ctoni_scores_lookup.get('conti_pc', 0) or 0) + (ctoni_scores_lookup.get('conti_pseq', 0) or 0)
    ctoni_gs_sum = (ctoni_scores_lookup.get('conti_ga', 0) or 0) + (ctoni_scores_lookup.get('conti_gc', 0) or 0) + (ctoni_scores_lookup.get('conti_gseq', 0) or 0)
    ctoni_fsiq_sum = ctoni_ps_sum + ctoni_gs_sum

    if ctoni_ps_sum and ctoni_ps_sum in RES['ctoni_pictorial_scale_sum_dict']:
        ctoni_ps_ss = RES['ctoni_pictorial_scale_sum_dict'][ctoni_ps_sum][0]
        if ctoni_ps_ss in RES['standard_score']:
            percentile = RES['standard_score'][ctoni_ps_ss][0]
            sl = RES['standard_score'][ctoni_ps_ss][1]
        else: percentile, sl = "", ""
        context.update({'ctoni_ps_sum': ctoni_ps_sum, 'ctoni_ps_ss': ctoni_ps_ss, 'ctoni_ps_percentile': percentile, 'ctoni_ps_sl': sl})
    else:
        context.update({'ctoni_ps_sum': "", 'ctoni_ps_ss': "", 'ctoni_ps_percentile': "", 'ctoni_ps_sl': ""})
    if ctoni_gs_sum and ctoni_gs_sum in RES['ctoni_geometric_scale_sum_dict']:
        ctoni_gs_ss = RES['ctoni_geometric_scale_sum_dict'][ctoni_gs_sum][0]
        if ctoni_gs_ss in RES['standard_score']:
            percentile = RES['standard_score'][ctoni_gs_ss][0]
            sl = RES['standard_score'][ctoni_gs_ss][1]
        else: percentile, sl = "", ""
        context.update({'ctoni_gs_sum': ctoni_gs_sum, 'ctoni_gs_ss': ctoni_gs_ss, 'ctoni_gs_percentile': percentile, 'ctoni_gs_sl': sl})
    else:
        context.update({'ctoni_gs_sum': "", 'ctoni_gs_ss': "", 'ctoni_gs_percentile': "", 'ctoni_gs_sl': ""})
    if ctoni_fsiq_sum and ctoni_fsiq_sum in RES['ctoni_full_scale_sum_dict']:
        ctoni_fsiq_ss = RES['ctoni_full_scale_sum_dict'][ctoni_fsiq_sum][0]
        if ctoni_fsiq_ss in RES['standard_score']:
            percentile = RES['standard_score'][ctoni_fsiq_ss][0]
            sl = RES['standard_score'][ctoni_fsiq_ss][1]
        else: percentile, sl = "", ""
        context.update({'ctoni_fsiq_sum': ctoni_fsiq_sum, 'ctoni_fsiq_ss': ctoni_fsiq_ss, 'ctoni_fsiq_percentile': percentile, 'ctoni_fsiq_sl': sl})
    else:
        context.update({'ctoni_fsiq_sum': "", 'ctoni_fsiq_ss': "", 'ctoni_fsiq_percentile': "", 'ctoni_fsiq_sl': ""})
       
    for subtest in context['wj_subtests']:
        context[subtest['name']] = subtest['score']
    context['wj_has_scores'] = any(test['score'] for test in context['wj_subtests'])
    wj_scores_lookup = {item['name']: item['score'] for item in context['wj_subtests']}
    for subtest in context['wj_subtests']:
        subtest_name = subtest['name']
        subtest_score = subtest['score']
        percentile_key = f"{subtest_name}_percentile"
        sl_key = f"{subtest_name}_sl"
        if subtest_score:    
            percentile = get_p_from_standard(RES['standard_score'], subtest_score)
            context[percentile_key] = percentile if percentile else ""
            skill_level = get_sl_from_standard(RES['standard_score'], subtest_score)
            context[sl_key] = skill_level if skill_level else ""
        else:
            context[sl_key] = ""
            context[percentile_key] = ""
                 
    for subtest in context['tvps4_subtests']:
        context[subtest['name']] = subtest['score']
    context['tvps4_has_scores'] = any(test['score'] for test in context['tvps4_subtests'])
    tvps4_scores_lookup = {item['name']: item['score'] for item in context['tvps4_subtests']}
    for subtest in context['tvps4_subtests']:
        subtest_name = subtest['name']
        subtest_score = subtest['score']
        percentile_key = f"{subtest_name}_percentile"
        sl_key = f"{subtest_name}_sl"
        if subtest_score:
            percentile = get_p_from_scaled(RES['scaled_score'], subtest_score)
            context[percentile_key] = percentile if percentile else ""
            skill_level = get_sl_from_scaled(RES['scaled_score'], subtest_score)
            context[sl_key] = skill_level if skill_level else ""
        else:
            context[percentile_key] = ""
            context[sl_key] = ""
    tvps4_sum = sum(val or 0 for val in tvps4_scores_lookup.values())
    if tvps4_sum and tvps4_sum in RES['tvps4_sum_standard_conversion']:
        tvps4_ss = RES['tvps4_sum_standard_conversion'][tvps4_sum][0]
        if tvps4_ss in RES['standard_score']:
            percentile = RES['standard_score'][tvps4_ss][0]
            sl = RES['standard_score'][tvps4_ss][1]
        else: percentile, sl = "", ""
        context.update({'tvps4_sum': tvps4_sum, 'tvps4_standard': tvps4_ss, 'tvps4_percentile': percentile, 'tvps4_overall_sl': sl})
    else:
        context.update({'tvps4_sum': "", 'tvps4_standard': "", 'tvps4_percentile': "", 'tvps4_overall_sl': ""})

    for subtest in context['taps4_subtests']:
        context[subtest['name']] = subtest['score']
    context['taps4_has_scores'] = any(test['score'] for test in context['taps4_subtests'])
    taps4_scores_lookup = {item['name']: item['score'] for item in context['taps4_subtests']}
    taps4_o_sum = sum(val or 0 for val in taps4_scores_lookup.values())
    taps4_pp_sum = (taps4_scores_lookup.get('taps4_wd', 0) or 0) + (taps4_scores_lookup.get('taps4_pd', 0) or 0) + (taps4_scores_lookup.get('taps4_pb', 0) or 0)
    taps4_am_sum = (taps4_scores_lookup.get('taps4_nmf', 0) or 0) + (taps4_scores_lookup.get('taps4_wm', 0) or 0) + (taps4_scores_lookup.get('taps4_sm', 0) or 0)
    taps4_lc_sum = (taps4_scores_lookup.get('taps4_pod', 0) or 0) + (taps4_scores_lookup.get('taps4_ac', 0) or 0)
    if taps4_o_sum and taps4_o_sum in RES['taps4_overall_sum_standard_conversion']:
        taps_overall_ss = RES['taps4_overall_sum_standard_conversion'][taps4_o_sum][0]
        if taps_overall_ss in RES['standard_score']:
            percentile = RES['standard_score'][taps_overall_ss][0]
            sl = RES['standard_score'][taps_overall_ss][1]
        else: percentile, sl = "", ""
        context.update({'taps4_o_sum': taps4_o_sum, 'taps4_overall_standard': taps_overall_ss, 'taps4_overall_percentile': percentile, 'taps4_overall_sl': sl})
    else:
        context.update({'taps4_o_sum': "", 'taps4_overall_standard': "", 'taps4_overall_percentile': "", 'taps4_overall_sl': ""})
    if taps4_pp_sum and taps4_pp_sum in RES['taps4_pp_am_sum_standard_conversion']:
        taps_pp_ss = RES['taps4_pp_am_sum_standard_conversion'][taps4_pp_sum][0]
        if taps_pp_ss in RES['standard_score']:
            percentile = RES['standard_score'][taps_pp_ss][0]
            sl = RES['standard_score'][taps_pp_ss][1]
        else: percentile, sl = "", ""
        context.update({'taps4_pp_sum': taps4_pp_sum, 'taps4_pp_standard': taps_pp_ss, 'taps4_pp_percentile': percentile, 'taps4_pp_sl': sl})
    else:
        context.update({'taps4_pp_sum': "", 'taps4_pp_standard': "", 'taps4_pp_percentile': "", 'taps4_pp_sl': ""})
    if taps4_am_sum and taps4_am_sum in RES['taps4_pp_am_sum_standard_conversion']:
        taps_am_ss = RES['taps4_pp_am_sum_standard_conversion'][taps4_am_sum][0]
        if taps_am_ss in RES['standard_score']:
            percentile = RES['standard_score'][taps_am_ss][0]
            sl = RES['standard_score'][taps_am_ss][1]
        else: percentile, sl = "", ""
        context.update({'taps4_am_sum': taps4_am_sum, 'taps4_am_standard': taps_am_ss, 'taps4_am_percentile': percentile, 'taps4_am_sl': sl})
    else:
        context.update({'taps4_am_sum': "", 'taps4_am_standard': "", 'taps4_am_percentile': "", 'taps4_am_sl': ""})
    if taps4_lc_sum and taps4_lc_sum in RES['taps4_lc_sum_standard_conversion']:
        taps_lc_ss = RES['taps4_lc_sum_standard_conversion'][taps4_lc_sum][0]
        if taps_lc_ss in RES['standard_score']:
            percentile = RES['standard_score'][taps_lc_ss][0]
            sl = RES['standard_score'][taps_lc_ss][1]
        else: percentile, sl = "", ""
        context.update({'taps4_lc_sum': taps4_lc_sum, 'taps4_lc_standard': taps_lc_ss, 'taps4_lc_percentile': percentile, 'taps4_lc_sl': sl})
    else:
        context.update({'taps4_lc_sum': "", 'taps4_lc_standard': "", 'taps4_lc_percentile': "", 'taps4_lc_sl': ""})
    for subtest in context['taps4_subtests']:
        subtest_name = subtest['name']
        subtest_score = subtest['score']
        percentile_key = f"{subtest_name}_percentile"
        sl_key = f"{subtest_name}_sl"
        if subtest_score:
            percentile = get_p_from_scaled(RES['scaled_score'], subtest_score)
            context[percentile_key] = percentile if percentile else ""
            skill_level = get_sl_from_scaled(RES['scaled_score'], subtest_score)
            context[sl_key] = skill_level if skill_level else ""
        else:
            context[percentile_key] = ""
            context[sl_key] = ""
    context['taps4_overall_desc'] = get_taps_phrase(context.get('taps4_overall_sl'), 'overall_concerns')
    context['taps4_wd_performance_desc'] = get_taps_phrase(context.get('taps4_wd_sl'), 'performance_verb')
    context['taps4_wd_conclusion_desc'] = get_taps_phrase(context.get('taps4_wd_sl'), 'conclusion')
    context['taps4_pd_performance_desc'] = get_taps_phrase(context.get('taps4_pd_sl'), 'performance_verb')
    context['taps4_nmf_performance_desc'] = get_taps_phrase(context.get('taps4_nmf_sl'), 'performance_verb')
    context['taps4_wm_performance_desc'] = get_taps_phrase(context.get('taps4_wm_sl'), 'performance_verb')

    for subtest in context['ctopp2_subtests']:
        context[subtest['name']] = subtest['score']
    context['ctopp2_has_scores'] = any(test['score'] for test in context['ctopp2_subtests'])
    ctopp2_scores_lookup = {item['name']: item['score'] for item in context['ctopp2_subtests']}
    pa_base_sum = (ctopp2_scores_lookup.get('ctopp2_elision', 0) or 0) + (ctopp2_scores_lookup.get('ctopp2_bw', 0) or 0)
    if age_years is not None and 4 <= age_years <= 6:
        ctopp2_pa_sum = pa_base_sum + (ctopp2_scores_lookup.get('ctopp2_sm', 0) or 0)
    elif age_years is not None and 7 <= age_years <= 24:
        ctopp2_pa_sum = pa_base_sum + (ctopp2_scores_lookup.get('ctopp2_pi', 0) or 0)
    else:
        ctopp2_pa_sum = pa_base_sum
    ctopp2_pm_sum = (ctopp2_scores_lookup.get('ctopp2_md', 0) or 0) + (ctopp2_scores_lookup.get('ctopp2_nr', 0) or 0)
    ctopp2_rsn_sum = (ctopp2_scores_lookup.get('ctopp2_rdn', 0) or 0) + (ctopp2_scores_lookup.get('ctopp2_rln', 0) or 0)
    ctopp2_rnsn_sum = (ctopp2_scores_lookup.get('ctopp2_rcn', 0) or 0) + (ctopp2_scores_lookup.get('ctopp2_ron', 0) or 0)
    
    if ctopp2_pa_sum and ctopp2_pa_sum in RES['ctopp2_sum_3_score']:
        score_data = RES['ctopp2_sum_3_score'][ctopp2_pa_sum]
        ss = score_data[0]
        percentile = score_data[1]
        sl = get_sl_from_standard(RES['standard_score'], ss) if ss in RES['standard_score'] else ""
        context.update({'ctopp2_pa_sum': ctopp2_pa_sum, 'ctopp2_pa_standard_score': ss, 'ctopp2_pa_percentile': percentile, 'ctopp2_pa_sl': sl})
    else:
        context.update({'ctopp2_pa_sum': "", 'ctopp2_pa_standard_score': "", 'ctopp2_pa_percentile': "", 'ctopp2_pa_sl': ""})
    if ctopp2_pm_sum and ctopp2_pm_sum in RES['ctopp2_sum_2_score']:
        score_data = RES['ctopp2_sum_2_score'][ctopp2_pm_sum]
        ss = score_data[0]
        percentile = score_data[1]
        sl = get_sl_from_standard(RES['standard_score'], ss) if ss in RES['standard_score'] else ""
        context.update({'ctopp2_pm_sum': ctopp2_pm_sum, 'ctopp2_pm_standard_score': ss, 'ctopp2_pm_percentile': percentile, 'ctopp2_pm_sl': sl})
    else:
        context.update({'ctopp2_pm_sum': "", 'ctopp2_pm_standard_score': "", 'ctopp2_pm_percentile': "", 'ctopp2_pm_sl': ""})
    if ctopp2_rsn_sum and ctopp2_rsn_sum in RES['ctopp2_sum_2_score']:
        score_data = RES['ctopp2_sum_2_score'][ctopp2_rsn_sum]
        ss = score_data[0]
        percentile = score_data[1]
        sl = get_sl_from_standard(RES['standard_score'], ss) if ss in RES['standard_score'] else ""
        context.update({'ctopp2_rsn_sum': ctopp2_rsn_sum, 'ctopp2_rsn_standard_score': ss, 'ctopp2_rsn_percentile': percentile, 'ctopp2_rsn_sl': sl})
    else:
        context.update({'ctopp2_rsn_sum': "", 'ctopp2_rsn_standard_score': "", 'ctopp2_rsn_percentile': "", 'ctopp2_rsn_sl': ""})
    if ctopp2_rnsn_sum and ctopp2_rnsn_sum in RES['ctopp2_sum_2_score']:
        score_data = RES['ctopp2_sum_2_score'][ctopp2_rnsn_sum]
        ss = score_data[0]
        percentile = score_data[1]
        sl = get_sl_from_standard(RES['standard_score'], ss) if ss in RES['standard_score'] else ""
        context.update({'ctopp2_rnsn_sum': ctopp2_rnsn_sum, 'ctopp2_rnsn_standard_score': ss, 'ctopp2_rnsn_percentile': percentile, 'ctopp2_rnsn_sl': sl})
    else:
        context.update({'ctopp2_rnsn_sum': "", 'ctopp2_rnsn_standard_score': "", 'ctopp2_rnsn_percentile': "", 'ctopp2_rnsn_sl': ""})
    pi_score = ctopp2_scores_lookup.get('ctopp2_pi')
    sm_score = ctopp2_scores_lookup.get('ctopp2_sm')

    for subtest in context['cas_subtests']:
        context[subtest['name']] = subtest['score']
    context['cas_has_scores'] = any(test['score'] for test in context['cas_subtests'])

    cas_scores_lookup = {item['name']: item['score'] for item in context['cas_subtests']}

    cas_planning_sum = (cas_scores_lookup.get('cas_pcodes', 0) or 0) + (cas_scores_lookup.get('cas_pcon', 0) or 0)
    cas_attention_sum = (cas_scores_lookup.get('cas_ea', 0) or 0) + (cas_scores_lookup.get('cas_nd', 0) or 0)
    cas_simultaneous_sum = (cas_scores_lookup.get('cas_matrices', 0) or 0) + (cas_scores_lookup.get('cas_vsr', 0) or 0)
    cas_successive_sum = (cas_scores_lookup.get('cas_ws', 0) or 0) + (cas_scores_lookup.get('cas_srq', 0) or 0)
    cas_fsiq_sum = cas_planning_sum + cas_attention_sum + cas_simultaneous_sum + cas_successive_sum
    cas_efwwm_sum = (cas_scores_lookup.get('cas_pcon', 0) or 0) + (cas_scores_lookup.get('cas_vsr', 0) or 0) + (cas_scores_lookup.get('cas_ea', 0) or 0) + (cas_scores_lookup.get('cas_srq', 0) or 0)
    cas_efwowm_sum = (cas_scores_lookup.get('cas_pcon', 0) or 0) + (cas_scores_lookup.get('cas_ea', 0) or 0)
    cas_wm_sum = (cas_scores_lookup.get('cas_vsr', 0) or 0) + (cas_scores_lookup.get('cas_srq', 0) or 0)
    cas_vc_sum = (cas_scores_lookup.get('cas_vsr', 0) or 0) + (cas_scores_lookup.get('cas_srq', 0) or 0)
    cas_nvc_sum = (cas_scores_lookup.get('cas_pcodes', 0) or 0) + (cas_scores_lookup.get('cas_matrices', 0) or 0) + (cas_scores_lookup.get('cas_fm', 0) or 0) 

    if cas_planning_sum and cas_planning_sum in RES['cas_planning_dict']:
        score_data = RES['cas_planning_dict'][cas_planning_sum]
        planning_ss = score_data[0]
        if planning_ss in RES['standard_score']:
            percentile = RES['standard_score'][planning_ss][0]
            sl = RES['standard_score'][planning_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_planning_sum': cas_planning_sum, 'cas_planning_ss': planning_ss, 'cas_planning_percentile': percentile, 'cas_planning_ci': score_data[3], 'cas_planning_sl': sl})
    else:
        context.update({'cas_planning_sum': "", 'cas_planning_ss': "", 'cas_planning_percentile': "", 'cas_planning_ci': "", 'cas_planning_sl': ""})
    if cas_attention_sum and cas_attention_sum in RES['cas_attention_dict']:
        score_data = RES['cas_attention_dict'][cas_attention_sum]
        attention_ss = score_data[0]
        if attention_ss in RES['standard_score']:
            percentile = RES['standard_score'][attention_ss][0]
            sl = RES['standard_score'][attention_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_attention_sum': cas_attention_sum, 'cas_attention_ss': attention_ss, 'cas_attention_percentile': percentile, 'cas_attention_ci': score_data[3], 'cas_attention_sl': sl})
    else:
        context.update({'cas_attention_sum': "", 'cas_attention_ss': "", 'cas_attention_percentile': "", 'cas_attention_ci': "", 'cas_attention_sl': ""})
    if cas_simultaneous_sum and cas_simultaneous_sum in RES['cas_simultaneous_dict']:
        score_data = RES['cas_simultaneous_dict'][cas_simultaneous_sum]
        simultaneous_ss = score_data[0]
        if simultaneous_ss in RES['standard_score']:
            percentile = RES['standard_score'][simultaneous_ss][0]
            sl = RES['standard_score'][simultaneous_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_simultaneous_sum': cas_simultaneous_sum, 'cas_simultaneous_ss': simultaneous_ss, 'cas_simultaneous_percentile': percentile, 'cas_simultaneous_ci': score_data[3], 'cas_simultaneous_sl': sl})
    else:
        context.update({'cas_simultaneous_sum': "", 'cas_simultaneous_ss': "", 'cas_simultaneous_percentile': "", 'cas_simultaneous_ci': "", 'cas_simultaneous_sl': ""})
    if cas_successive_sum and cas_successive_sum in RES['cas_successive_dict']:
        score_data = RES['cas_successive_dict'][cas_successive_sum]
        successive_ss = score_data[0]
        if successive_ss in RES['standard_score']:
            percentile = RES['standard_score'][successive_ss][0]
            sl = RES['standard_score'][successive_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_successive_sum': cas_successive_sum, 'cas_successive_ss': successive_ss, 'cas_successive_percentile': percentile, 'cas_successive_ci': score_data[3], 'cas_successive_sl': sl})
    else:
        context.update({'cas_successive_sum': "", 'cas_successive_ss': "", 'cas_successive_percentile': "", 'cas_successive_ci': "", 'cas_successive_sl': ""})
    if cas_fsiq_sum and cas_fsiq_sum in RES['cas_fsiq_dict']:
        score_data = RES['cas_fsiq_dict'][cas_fsiq_sum]
        fsiq_ss = score_data[0]
        if fsiq_ss in RES['standard_score']:
            percentile = RES['standard_score'][fsiq_ss][0]
            sl = RES['standard_score'][fsiq_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_fsiq_sum': cas_fsiq_sum, 'cas_fsiq_ss': fsiq_ss, 'cas_fsiq_percentile': percentile, 'cas_fsiq_ci': score_data[3], 'cas_fsiq_sl': sl})
    else:
        context.update({'cas_fsiq_sum': "", 'cas_fsiq_ss': "", 'cas_fsiq_percentile': "", 'cas_fsiq_ci': "", 'cas_fsiq_sl': ""})
    if cas_efwwm_sum and cas_efwwm_sum in RES['cas_efwwm_dict']:
        score_data = RES['cas_efwwm_dict'][cas_efwwm_sum]
        efwwm_ss = score_data[0]
        if efwwm_ss in RES['standard_score']:
            percentile = RES['standard_score'][efwwm_ss][0]
            sl = RES['standard_score'][efwwm_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_efwwm_sum': cas_efwwm_sum, 'cas_efwwm_ss': efwwm_ss, 'cas_efwwm_percentile': percentile, 'cas_efwwm_ci': score_data[3], 'cas_efwwm_sl': sl})
    else:
        context.update({'cas_efwwm_sum': "", 'cas_efwwm_ss': "", 'cas_efwwm_percentile': "", 'cas_efwwm_ci': "", 'cas_efwwm_sl': ""})
    if cas_efwowm_sum and cas_efwowm_sum in RES['cas_efwowm_dict']:
        score_data = RES['cas_efwowm_dict'][cas_efwowm_sum]
        efwowm_ss = score_data[0]
        if efwowm_ss in RES['standard_score']:
            percentile = RES['standard_score'][efwowm_ss][0]
            sl = RES['standard_score'][efwowm_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_efwowm_sum': cas_efwowm_sum, 'cas_efwowm_ss': efwowm_ss, 'cas_efwowm_percentile': percentile, 'cas_efwowm_ci': score_data[3], 'cas_efwowm_sl': sl})
    else:
        context.update({'cas_efwowm_sum': "", 'cas_efwowm_ss': "", 'cas_efwowm_percentile': "", 'cas_efwowm_ci': "", 'cas_efwowm_sl': ""})
    if cas_wm_sum and cas_wm_sum in RES['cas_wm_dict']:
        score_data = RES['cas_wm_dict'][cas_wm_sum]
        wm_ss = score_data[0]
        if wm_ss in RES['standard_score']:
            percentile = RES['standard_score'][wm_ss][0]
            sl = RES['standard_score'][wm_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_wm_sum': cas_wm_sum, 'cas_wm_ss': wm_ss, 'cas_wm_percentile': percentile, 'cas_wm_ci': score_data[3], 'cas_wm_sl': sl})
    else:
        context.update({'cas_wm_sum': "", 'cas_wm_ss': "", 'cas_wm_percentile': "", 'cas_wm_ci': "", 'cas_wm_sl': ""})
    if cas_vc_sum and cas_vc_sum in RES['cas_vc_dict']:
        score_data = RES['cas_vc_dict'][cas_vc_sum]
        vc_ss = score_data[0]
        if vc_ss in RES['standard_score']:
            percentile = RES['standard_score'][vc_ss][0]
            sl = RES['standard_score'][vc_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_vc_sum': cas_vc_sum, 'cas_vc_ss': vc_ss, 'cas_vc_percentile': percentile, 'cas_vc_ci': score_data[3], 'cas_vc_sl': sl})
    else:
        context.update({'cas_vc_sum': "", 'cas_vc_ss': "", 'cas_vc_percentile': "", 'cas_vc_ci': "", 'cas_vc_sl': ""})
    if cas_nvc_sum and cas_nvc_sum in RES['cas_nvc_dict']:
        score_data = RES['cas_nvc_dict'][cas_nvc_sum]
        nvc_ss = score_data[0]
        if nvc_ss in RES['standard_score']:
            percentile = RES['standard_score'][nvc_ss][0]
            sl = RES['standard_score'][nvc_ss][1]
        else: percentile, sl = "", ""
        context.update({'cas_nvc_sum': cas_nvc_sum, 'cas_nvc_ss': nvc_ss, 'cas_nvc_percentile': percentile, 'cas_nvc_ci': score_data[3], 'cas_nvc_sl': sl})
    else:
        context.update({'cas_nvc_sum': "", 'cas_nvc_ss': "", 'cas_nvc_percentile': "", 'cas_nvc_ci': "", 'cas_nvc_sl': ""})

    for subtest in context['wraml_subtests']:
        context[subtest['name']] = subtest['score']
    for subtest in context['wraml_subtests']:
        subtest_name = subtest['name']
        subtest_score = subtest['score']
        sl_key = f"{subtest_name}_sl"
        if subtest_score:    
            skill_level = get_sl_from_scaled(RES['scaled_score'], subtest_score)
            context[sl_key] = skill_level if skill_level else ""
        else:
            context[sl_key] = ""
    context['wraml_has_scores'] = any(test['score'] for test in context['wraml_subtests'])
    wraml_scores_lookup = {item['name']: item['score'] for item in context['wraml_subtests']}
    visualim_sum = (wraml_scores_lookup.get('wraml_pm', 0) or 0) + (wraml_scores_lookup.get('wraml_dl', 0) or 0)
    verbalim_sum = (wraml_scores_lookup.get('wraml_sm', 0) or 0) + (wraml_scores_lookup.get('wraml_vl', 0) or 0)
    ac_sum = (wraml_scores_lookup.get('wraml_fw', 0) or 0) + (wraml_scores_lookup.get('wraml_nl', 0) or 0)
    gmi_sum = visualim_sum + verbalim_sum + ac_sum
    
    if visualim_sum and visualim_sum in RES['wraml_visualim_dict']:
        score_data = RES['wraml_visualim_dict'][visualim_sum]
        visualim_ss = score_data[0]
        visualim_sl = RES['standard_score'][visualim_ss][1] if visualim_ss in RES['standard_score'] else ""
        context.update({'visualim_sum': visualim_sum, 'visualim_ss': visualim_ss, 'visualim_percentile': score_data[1], 'visualim_ci': score_data[3], 'visualim_sl': visualim_sl})
    else:
        context.update({'visualim_sum': "", 'visualim_ss': "", 'visualim_percentile': "", 'visualim_ci': "", 'visualim_sl': ""})
    if verbalim_sum and verbalim_sum in RES['wraml_verbalim_dict']:
        score_data = RES['wraml_verbalim_dict'][verbalim_sum]
        verbalim_ss = score_data[0]
        verbalim_sl = RES['standard_score'][verbalim_ss][1] if verbalim_ss in RES['standard_score'] else ""
        context.update({'verbalim_sum': verbalim_sum, 'verbalim_ss': verbalim_ss, 'verbalim_percentile': score_data[1], 'verbalim_ci': score_data[3], 'verbalim_sl': verbalim_sl})
    else:
        context.update({'verbalim_sum': "", 'verbalim_ss': "", 'verbalim_percentile': "", 'verbalim_ci': "", 'verbalim_sl': ""})
    if ac_sum and ac_sum in RES['wraml_ac_dict']:
        score_data = RES['wraml_ac_dict'][ac_sum]
        ac_ss = score_data[0]
        ac_sl = RES['standard_score'][ac_ss][1] if ac_ss in RES['standard_score'] else ""
        context.update({'ac_sum': ac_sum, 'ac_ss': ac_ss, 'ac_percentile': score_data[1], 'ac_ci': score_data[3], 'ac_sl': ac_sl})
    else:
        context.update({'ac_sum': "", 'ac_ss': "", 'ac_percentile': "", 'ac_ci': "", 'ac_sl': ""})
    if gmi_sum and gmi_sum in RES['wraml_gmi_dict']:
        score_data = RES['wraml_gmi_dict'][gmi_sum]
        gmi_ss = score_data[0]
        gmi_sl = RES['standard_score'][gmi_ss][1] if gmi_ss in RES['standard_score'] else ""
        context.update({'gmi_sum': gmi_sum, 'gmi_ss': gmi_ss, 'gmi_percentile': score_data[1], 'gmi_ci': score_data[3], 'gmi_sl': gmi_sl})
    else:
        context.update({'gmi_sum': "", 'gmi_ss': "", 'gmi_percentile': "", 'gmi_ci': "", 'gmi_sl': ""})

    kabc_age_dicts = {
        4: {'gsm': RES['sequential_gsm_dict_age4'], 'gv': RES['simultaneous_gv_dict_age4'], 'glr': RES['learning_glr_dict_age4'], 'gc': RES['knowledge_gc_dict_age4'], 'mpi': RES['mpi_dict_age4'], 'fci': RES['fci_dict_age4']},
        5: {'gsm': RES['sequential_gsm_dict_age5'], 'gv': RES['simultaneous_gv_dict_age5'], 'glr': RES['learning_glr_dict_age5'], 'gc': RES['knowledge_gc_dict_age5'], 'mpi': RES['mpi_dict_age5'], 'fci': RES['fci_dict_age5']},
        6: {'gsm': RES['sequential_gsm_dict_age6'], 'gv': RES['simultaneous_gv_dict_age6'], 'glr': RES['learning_glr_dict_age6'], 'gc': RES['knowledge_gc_dict_age6'], 'mpi': RES['mpi_dict_age6'], 'fci': RES['fci_dict_age6']}
    }
    for subtest in context['kabc_subtests']:
        context[subtest['name']] = subtest['score']
    context['kabc_has_scores'] = any(test['score'] for test in context['kabc_subtests'])
    kabc_scores_lookup = {item['name']: item['score'] for item in context['kabc_subtests']}
    gsm_sum = (kabc_scores_lookup.get('kabc_nr', 0) or 0) + (kabc_scores_lookup.get('kabc_wo', 0) or 0)
    glr_sum = (kabc_scores_lookup.get('kabc_atlantis', 0) or 0) + (kabc_scores_lookup.get('kabc_rebus', 0) or 0)
    gv_sum = (kabc_scores_lookup.get('kabc_rover', 0) or 0) + (kabc_scores_lookup.get('kabc_t', 0) or 0)
    gc_sum = (kabc_scores_lookup.get('kabc_vk', 0) or 0) + (kabc_scores_lookup.get('kabc_riddles', 0) or 0)
    mpi_sum = gsm_sum + glr_sum + gv_sum
    fci_sum = gsm_sum + glr_sum + gv_sum + gc_sum
    context.update({'kabc_gsm_sum': gsm_sum, 'kabc_glr_sum': glr_sum, 'kabc_gv_sum': gv_sum, 'kabc_gc_sum': gc_sum, 'kabc_mpi_sum': mpi_sum, 'kabc_fci_sum': fci_sum})
    active_dicts = kabc_age_dicts.get(age_years)
    if gsm_sum and active_dicts and gsm_sum in active_dicts.get('gsm', {}):
        score_data = active_dicts['gsm'][gsm_sum]
        gsm_ss = score_data[0]
        scores = get_standard_sl_p(RES['standard_score'], gsm_ss)
        gsm_percentile, gsm_sl = scores if scores else ("", "")
        context.update({'kabc_gsm_ss': gsm_ss, 'kabc_gsm_ci': score_data[2], 'kabc_gsm_percntile': gsm_percentile, 'kabc_gsm_sl': gsm_sl})
    else:
        context.update({'kabc_gsm_ss': "", 'kabc_gsm_ci': "", 'kabc_gsm_percntile': "", 'kabc_gsm_sl': ""})
    if glr_sum and active_dicts and glr_sum in active_dicts.get('glr', {}):
        score_data = active_dicts['glr'][glr_sum]
        glr_ss = score_data[0]
        scores = get_standard_sl_p(RES['standard_score'], glr_ss)
        glr_percentile, glr_sl = scores if scores else ("", "")
        context.update({'kabc_glr_ss': glr_ss, 'kabc_glr_ci': score_data[2], 'kabc_glr_percntile': glr_percentile, 'kabc_glr_sl': glr_sl})
    else:
        context.update({'kabc_glr_ss': "", 'kabc_glr_ci': "", 'kabc_glr_percntile': "", 'kabc_glr_sl': ""})
    if gv_sum and active_dicts and gv_sum in active_dicts.get('gv', {}):
        score_data = active_dicts['gv'][gv_sum]
        gv_ss = score_data[0]
        scores = get_standard_sl_p(RES['standard_score'], gv_ss)
        gv_percentile, gv_sl = scores if scores else ("", "")
        context.update({'kabc_gv_ss': gv_ss, 'kabc_gv_ci': score_data[2], 'kabc_gv_percntile': gv_percentile, 'kabc_gv_sl': gv_sl})
    else:
        context.update({'kabc_gv_ss': "", 'kabc_gv_ci': "", 'kabc_gv_percntile': "", 'kabc_gv_sl': ""})
    if gc_sum and active_dicts and gc_sum in active_dicts.get('gc', {}):
        score_data = active_dicts['gc'][gc_sum]
        gc_ss = score_data[0]
        scores = get_standard_sl_p(RES['standard_score'], gc_ss)
        gc_percentile, gc_sl = scores if scores else ("", "")
        context.update({'kabc_gc_ss': gc_ss, 'kabc_gc_ci': score_data[2], 'kabc_gc_percntile': gc_percentile, 'kabc_gc_sl': gc_sl})
    else:
        context.update({'kabc_gc_ss': "", 'kabc_gc_ci': "", 'kabc_gc_percntile': "", 'kabc_gc_sl': ""})
    if gc_sum and active_dicts:
        context['kabc_overall_name'] = "Fluid-Crystallized Index (FCI)"
        fci_sum_val = context.get('kabc_fci_sum')
        if fci_sum_val and fci_sum_val in active_dicts.get('fci', {}):
            score_data = active_dicts['fci'][fci_sum_val]
            fci_ss = score_data[0]
            scores = get_standard_sl_p(RES['standard_score'], fci_ss)
            fci_percentile, fci_sl = scores if scores else ("", "")
            context.update({'kabc_fci_ss': fci_ss, 'kabc_fci_ci': score_data[2], 'kabc_fci_percentile': fci_percentile, 'kabc_fci_sl': fci_sl})
        else:
            context.update({'kabc_fci_ss': "", 'kabc_fci_ci': "", 'kabc_fci_percentile': "", 'kabc_fci_sl': ""})
        context.update({'kabc_mpi_ss': "", 'kabc_mpi_ci': "", 'kabc_mpi_percentile': "", 'kabc_mpi_sl': ""})
    else:
        context['kabc_overall_name'] = "Mental Processing Index (MPI)"
        mpi_sum_val = context.get('kabc_mpi_sum')
        if mpi_sum_val and active_dicts and mpi_sum_val in active_dicts.get('mpi', {}):
            score_data = active_dicts['mpi'][mpi_sum_val]
            mpi_ss = score_data[0]
            scores = get_standard_sl_p(RES['standard_score'], mpi_ss)
            mpi_percentile, mpi_sl = scores if scores else ("", "")
            context.update({'kabc_mpi_ss': mpi_ss, 'kabc_mpi_ci': score_data[2], 'kabc_mpi_percentile': mpi_percentile, 'kabc_mpi_sl': mpi_sl})
        else:
            context.update({'kabc_mpi_ss': "", 'kabc_mpi_ci': "", 'kabc_mpi_percentile': "", 'kabc_mpi_sl': ""})
        context.update({'kabc_fci_ss': "", 'kabc_fci_ci': "", 'kabc_fci_percentile': "", 'kabc_fci_sl': ""})

    kabc_nvi_age_dicts = {4: RES['nvi_dict_age4'], 5: RES['nvi_dict_age5'], 6: RES['nvi_dict_age6']}
    for subtest in context['kabc_nv_subtests']:
        context[subtest['name']] = subtest['score']
    context['kabc_nv_has_scores'] = any(test['score'] for test in context['kabc_nv_subtests'])
    kabc_nv_scores_lookup = {item['name']: item['score'] for item in context['kabc_nv_subtests']}
    
    
    kabc_nvi_sum = (kabc_nv_scores_lookup.get('kabc_nv_sc', 0) or 0) + \
                   (kabc_nv_scores_lookup.get('kabc_nv_triangles', 0) or 0) + \
                   (kabc_nv_scores_lookup.get('kabc_nv_bc', 0) or 0) + \
                   (kabc_nv_scores_lookup.get('kabc_nv_pr', 0) or 0) + \
                   (kabc_nv_scores_lookup.get('kabc_nv_hm', 0) or 0)
    context['kabc_nvi_sum'] = kabc_nvi_sum
    active_nvi_dict = kabc_nvi_age_dicts.get(age_years)
    
    if kabc_nvi_sum and active_nvi_dict and kabc_nvi_sum in active_nvi_dict:
        score_data = active_nvi_dict[kabc_nvi_sum]
        nvi_ss = score_data[0]
        nvi_ci = score_data[2] 
        scores = get_standard_sl_p(RES['standard_score'], nvi_ss)
        nvi_percentile, nvi_sl = scores if scores else ("", "")
        context.update({'kabc_nvi_ss': nvi_ss, 'kabc_nvi_ci': nvi_ci, 'kabc_nvi_percentile': nvi_percentile, 'kabc_nvi_sl': nvi_sl})
    else:
        context.update({'kabc_nvi_ss': "", 'kabc_nvi_ci': "", 'kabc_nvi_percentile': "", 'kabc_nvi_sl': ""})
    
    student_skill_level = context.get('kabc_nvi_sl')
    descriptor_key = 'nvi_performance_descriptor'
    if student_skill_level in ["Low", "Very Low"]:
        descriptor = "significantly inhibit learning and performance."
    elif student_skill_level in ["Low Average", "Below Average"]:
        descriptor = "may create inconsistencies or inhibit learning and performance."
    elif student_skill_level == "Average":
        descriptor = "are adequate to support learning and performance."
    elif student_skill_level in ["High Average", "Above Average"]:
        descriptor = "facilitate learning and performance."
    elif student_skill_level in ["High", "Very High"]:
        descriptor = "are a significant strength and facilitates learning and performance."
    else:
        descriptor = "could not be determined based on this assessment."
    context[descriptor_key] = descriptor

    for subtest in context['wnv_subtests']:
        context[subtest['name']] = subtest['score']
    context['wnv_has_scores'] = any(test['score'] for test in context['wnv_subtests'])
    wnv_scores_lookup = {item['name']: item['score'] for item in context['wnv_subtests']}
    if age_years is not None:
        if 4 <= age_years <= 7:
            nai_sum = (wnv_scores_lookup.get('wnv_mr', 0) or 0) + (wnv_scores_lookup.get('wnv_coding', 0) or 0) + (wnv_scores_lookup.get('wnv_oa', 0) or 0) + (wnv_scores_lookup.get('wnv_recognition', 0) or 0)
        elif 8 <= age_years <= 21:
            nai_sum = (wnv_scores_lookup.get('wnv_mr', 0) or 0) + (wnv_scores_lookup.get('wnv_coding', 0) or 0) + (wnv_scores_lookup.get('wnv_ss', 0) or 0) + (wnv_scores_lookup.get('wnv_pa', 0) or 0)
        else:
            nai_sum = 0
    else:
        nai_sum = 0
    if nai_sum and nai_sum in RES['wnv_dict']:
        score_data = RES['wnv_dict'][nai_sum]
        nai_ss_value = score_data[0]
        if nai_ss_value in RES['standard_score']:
            nai_percentile = RES['standard_score'][nai_ss_value][0]
            nai_sl = RES['standard_score'][nai_ss_value][1]
        else:
            nai_percentile, nai_sl = "", ""
        context.update({'nai_sum': nai_sum, 'nai_ss': nai_ss_value, 'nai_ci': score_data[3], 'nai_percentile': nai_percentile, 'nai_sl': nai_sl})
    else:
        context.update({'nai_sum': "", 'nai_ss': "", 'nai_ci': "", 'nai_percentile': "", 'nai_sl': ""})
    for subtest in context['wnv_subtests']:
        subtest_name = subtest['name']
        subtest_score = subtest['score']
        percentile_key = f"{subtest_name}_percentile"
        sl_key = f"{subtest_name}_sl"
        if subtest_score:
            percentile = get_p_from_tscore(RES['t_score'], subtest_score)
            context[percentile_key] = percentile if percentile else ""
            skill_level = get_sl_from_tscore(RES['t_score'], subtest_score)
            context[sl_key] = skill_level if skill_level else ""
        else:
            context[percentile_key] = ""
            context[sl_key] = ""
    
    try:
        root_path = RES.get('root_dir', os.getcwd()) 
        template_dir = os.path.join(root_path, "docx_templates")
        report_sections = [
            # YOU MUST UPDATE THIS LIST
            ('JPU_Report_Template_Intro.docx', True), 
            ('JPU_Report_Template_Wisc.docx', context.get('wisc_has_scores', False)),
            ('JPU_Report_Template_Ctoni.docx', context.get('ctoni_has_scores', False)),
            ('JPU_Report_Template_Wj.docx', context.get('wj_has_scores', False)),
            ('JPU_Report_Template_Tvps4.docx', context.get('tvps4_has_scores', False)),
            ('JPU_Report_Template_Taps4.docx', context.get('taps4_has_scores', False)),
            ('JPU_Report_Template_Vmi.docx', context.get('vmi_has_scores', False)),
            ('JPU_Report_Template_Ctopp2.docx', context.get('ctopp2_has_scores', False)),
            ('JPU_Report_Template_Cas.docx', context.get('cas_has_scores', False)),
            ('JPU_Report_Template_Wraml.docx', context.get('wraml_has_scores', False)),
            ('JPU_Report_Template_Kabc.docx', context.get('kabc_has_scores', False)),
            ('JPU_Report_Template_Kabc_Nv.docx', context.get('kabc_nv_has_scores', False)),
            ('JPU_Report_Template_Wnv.docx', context.get('wnv_has_scores', False))
        ]

        st.info("Assembling report... Please wait.")

        # --- 3. Render the Base Document ---
        base_template_name = report_sections[0][0]
        st.write(f"Building base: {base_template_name}...")
        
        base_doc = DocxTemplate(os.path.join(template_dir, base_template_name))
        base_doc.render(context)
        
        composer = Composer(base_doc)

        for template_name, is_included in report_sections[1:]:
            
            if is_included:
                st.write(f"Appending: {template_name}...")
                
                tpl_path = os.path.join(template_dir, template_name)
                sub_doc = DocxTemplate(tpl_path)
                sub_doc.render(context)
                composer.append(sub_doc)

        st.info("Finalizing document...")
        bio = io.BytesIO()
        composer.save(bio)
        
        st.success("✅ Report Assembled Successfully!")
        st.download_button(
            label="Click here to Download DOCX",
            data=bio.getvalue(),
            file_name=f"{context['name']}_report.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except FileNotFoundError as e:
        st.error(f"FILE NOT FOUND ERROR: Could not find template file.")
        st.error(f"Details: {e}")
        st.error(f"Please check your 'docx_templates' folder.")
    except Exception as e:
        st.error(f"An error occurred while generating the document: {e}")
        st.error(f"DEBUG: Root path was set to: {root_path}")

    st.divider()
    st.header("Data Validation Warnings")
    
    ctopp_scores_entered = context.get('ctopp2_has_scores')

    if pi_score and sm_score:
        st.warning(
            "**CTOPP-2 Warning:**\n"
            "  - Issue: Both 'Phoneme Isolation' and 'Sound Matching' have scores.\n"
            "  - Action: Only one should be administered. The script will proceed based on age."
        )
    elif age_years is not None and age_years < 4 and ctopp_scores_entered:
        st.warning(
            "**CTOPP-2 Warning:**\n"
            f"  - Student age: {age_years} years, {age_months} months.\n"
            "  - Issue: CTOPP-2 scores were entered, but the test is only for ages 4-24."
        )
    elif age_years is not None and 4 <= age_years <= 6 and pi_score:
        st.warning(
            "**CTOPP-2 Warning:**\n"
            f"  - Student age: {age_years} years, {age_months} months.\n"
            f"  - Issue: CTOPP2 'Phoneme Isolation' (for ages 8+) was given, but student is {age_years} years and {age_months} months old."
        )
    elif age_years is not None and 7 <= age_years <= 24 and sm_score:
        st.warning(
            "**CTOPP-2 Warning:**\n"
            f"  - Student age: {age_years} years, {age_months} months.\n"
            f"  - Issue: CTOPP2 'Sound Matching' (for ages 4-6) was given, but student is {age_years} years and {age_months} months old."
        )
    

    if context['kabc_has_scores'] and (age_years is None or not (4 <= age_years <= 6)):
        st.warning(
            "**KABC-II Warning:**\n"
            f"  - Age: {age_years}\n"
            "  - Issue: KABC-II scores were entered, but the student's age is outside the valid 4-6 year range for this lookup table.\n"
            "  - Action: Composite scores will not be calculated."
        )

    if context['kabc_nv_has_scores'] and (age_years is None or not (4 <= age_years <= 6)):
        st.warning(
            "**KABC-II NV Warning:**\n"
            f"  - Age: {age_years}\n"
            "  - Issue: KABC-II NV scores were entered, but the student's age is outside the valid 4-6 year range for this lookup table.\n"
            "  - Action: Composite scores will not be calculated."
        )

    wnv_scores_entered = context.get('wnv_has_scores')
    spatial_span_score = wnv_scores_lookup.get('wnv_ss')
    picture_arrangement_score = wnv_scores_lookup.get('wnv_pa')
    recognition_score = wnv_scores_lookup.get('wnv_recognition')
    object_assembly_score = wnv_scores_lookup.get('wnv_oa')

    if age_years is not None:
        if age_years < 4 and wnv_scores_entered:
            st.warning(
                "**WNV Age Warning:**\n"
                f"  - Student age: {age_years} years, {age_months} months\n"
                "  - Issue: WNV scores were entered, but the test is only for ages 4-21.\n"
                "  - Action: No WNV scores will be calculated."
            )
        if 4 <= age_years <= 7 and (spatial_span_score or picture_arrangement_score):
            st.warning(
                "**WNV Warning:**\n"
                f"  - Age: {age_years} years, {age_months} months\n"
                f"  - Issue: WNV Spatial Span or Picture Arrangement (for ages 8-21) subtest was given a score, but student is {age_years} years old.\n"
                "  - Note: This score will be ignored in the NAI sum calculation."
            )
        elif age_years >= 8 and (recognition_score or object_assembly_score):
            st.warning(
                "**WNV Warning:**\n"
                f"  - Age: {age_years} years, {age_months} months\n"
                f"  - Issue: WNV Recognition or Object Assembly (for ages 4-7) subtest was given a score, but student is {age_years} years old.\n"
                "  - Note: This score will be ignored in the NAI sum calculation."
            )
    #generate_all_visuals(context)