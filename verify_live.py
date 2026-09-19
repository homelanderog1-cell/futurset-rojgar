import requests

base_url = 'http://127.0.0.1:8000'

print('--- CHECK 1: /health ---')
r = requests.get(base_url + '/health')
print('Status:', r.status_code, r.json())
assert r.status_code == 200
data = r.json()
assert data['status'] == 'healthy' and data['brand'] == 'FuturSet'

print('\n--- CHECK 2: Main Homepage / ---')
r = requests.get(base_url + '/')
print('Status:', r.status_code, 'Bytes:', len(r.text))
assert r.status_code == 200
assert 'FuturSet' in r.text
assert 'startLiveScan' in r.text
assert 'syllabus-modal' in r.text
assert 'fee-guide-modal' in r.text
assert 'timeline-modal' in r.text
assert 'filter-pill-sector' in r.text
assert 'resetAllFilters' in r.text

print('\n--- CHECK 3: Dedicated Gujarat Portal /gujarat ---')
r = requests.get(base_url + '/gujarat')
print('Status:', r.status_code, 'Bytes:', len(r.text))
assert r.status_code == 200
assert 'ગુજરાત' in r.text
assert 'OJAS' in r.text
assert 'syllabus-modal' in r.text, "Must have syllabus-modal in Gujarat portal"
assert 'fee-guide-modal' in r.text, "Must have fee-guide-modal in Gujarat portal"
assert 'timeline-modal' in r.text, "Must have timeline-modal in Gujarat portal"
assert 'filter-pill-gujarat' in r.text, "Must have filter-pill-gujarat in Gujarat portal"
assert 'scanner-radar-icon' in r.text, "Must have scanner-radar-icon ID to prevent JS error"
assert 'openMatcherModal' in r.text, "Must have AI Matcher button on Gujarat portal"
assert 'openBookmarksModal' in r.text, "Must have Bookmarks button on Gujarat portal"
assert 'btn-view-cards' in r.text and 'btn-view-table' in r.text, "Must have view mode switcher"

print('\n--- CHECK 4: Static Assets ---')
css = requests.get(base_url + '/static/css/style.css')
js_app = requests.get(base_url + '/static/js/app.js')
js_scan = requests.get(base_url + '/static/js/scanner.js')
print('CSS Status:', css.status_code, 'App.js Status:', js_app.status_code, 'Scanner.js Status:', js_scan.status_code)
assert css.status_code == 200 and js_app.status_code == 200 and js_scan.status_code == 200
assert 'copyJobLink' in js_app.text
assert 'radarIcon' in js_scan.text

print('\n--- CHECK 5: API Stats ---')
r = requests.get(base_url + '/api/stats')
stats = r.json()
print('Stats:', stats)
assert r.status_code == 200
assert stats['total_jobs'] >= 20
assert stats['gujarat_jobs'] >= 10

print('\n--- CHECK 6: Gujarat Filtered Jobs ---')
r = requests.get(base_url + '/api/jobs?state=Gujarat')
jobs = r.json()
print('Total Gujarat Jobs:', jobs['count'])
for j in jobs['results'][:3]:
    print(' - [' + j['board_category'] + '] ' + j['title'] + ' (' + str(j['vacancies']) + ' posts)')
assert jobs['count'] >= 10

print('\n--- CHECK 7: Central Government Filtered Jobs ---')
r = requests.get(base_url + '/api/jobs?gov_level=Central')
cen_jobs = r.json()
print('Total Central Jobs:', cen_jobs['count'])
assert cen_jobs['count'] >= 8

print('\n--- CHECK 8: AI Career Matcher (Eligible Candidate) ---')
match_payload = {
    'age': 23,
    'qualification': 'Graduate',
    'category': 'OBC/SEBC',
    'state_preference': 'Gujarat',
    'include_central': True
}
r = requests.post(base_url + '/api/match', json=match_payload)
matches = r.json()
print('Matched recommendations:', len(matches))
top = matches[0]
print('Top Match: ' + top['job']['title'] + ' -> Score: ' + str(top['match_score']) + '%, Status: ' + top['eligibility_status'])
assert len(matches) > 0
assert top['match_score'] >= 80

print('\n--- CHECK 9: AI Matcher Underage Disqualification Boundary ---')
minor_payload = {
    'age': 15,  # Statutory underage
    'qualification': '10th Pass',
    'category': 'General',
    'state_preference': 'Gujarat'
}
r = requests.post(base_url + '/api/match', json=minor_payload)
minor_matches = r.json()
assert len(minor_matches) > 0
print('15yo Top Match Status:', minor_matches[0]['eligibility_status'], 'Score:', minor_matches[0]['match_score'])
assert all(m['eligibility_status'] == 'Ineligible (Underage)' for m in minor_matches)
assert all(m['match_score'] <= 20 for m in minor_matches)

print('\n--- CHECK 10: AI Matcher Overage Disqualification Boundary ---')
overage_payload = {
    'age': 65,  # Strictly overage
    'qualification': 'Graduate',
    'category': 'General',
    'state_preference': 'Gujarat'
}
r = requests.post(base_url + '/api/match', json=overage_payload)
over_matches = r.json()
assert len(over_matches) > 0
print('65yo Top Match Status:', over_matches[0]['eligibility_status'], 'Score:', over_matches[0]['match_score'])
assert all(m['eligibility_status'] == 'Ineligible (Exceeds Age Limit)' for m in over_matches)
assert all(m['match_score'] <= 20 for m in over_matches)

print('\n--- CHECK 11: AI Matcher Medical Discipline Safety ---')
non_med_payload = {
    'age': 28,
    'qualification': 'Post Graduate',  # Non-MBBS
    'category': 'General',
    'state_preference': 'Gujarat'
}
r = requests.post(base_url + '/api/match', json=non_med_payload)
non_med_matches = r.json()
med_results = [m for m in non_med_matches if 'Medical' in m['job']['title'] or 'MBBS' in m['job']['title']]
print('Medical jobs found:', len(med_results))
for mr in med_results:
    print(' - ' + mr['job']['title'] + ' -> ' + mr['eligibility_status'])
    assert mr['eligibility_status'] == 'Ineligible (Qualification Shortfall)'
    assert mr['match_score'] <= 30

print('\n--- CHECK 12: Live Scanner Sync Execution ---')
r = requests.post(base_url + '/api/scan/start')
scan_res = r.json()
print('Scan Result status:', scan_res['scan_result']['status'], 'Scanned:', scan_res['scan_result']['scanned'])
assert r.status_code == 200
assert scan_res['scan_result']['status'] == 'success'
assert scan_res['scan_result']['scanned'] > 0

print('\n--- CHECK 13: Bookmark Toggle Lifecycle ---')
r_jobs = requests.get(base_url + '/api/jobs?limit=1')
target_id = r_jobs.json()['results'][0]['id']
# Ensure state starts known: if already bookmarked, toggle once to clear
r_list_init = requests.get(base_url + '/api/bookmarks')
if any(b['id'] == target_id for b in r_list_init.json()['bookmarks']):
    requests.post(base_url + f'/api/bookmark/{target_id}')

# Toggle ON
r_bm_on = requests.post(base_url + f'/api/bookmark/{target_id}', json={'notes': 'Live test note'})
assert r_bm_on.status_code == 200
assert r_bm_on.json()['is_bookmarked'] is True

r_list = requests.get(base_url + '/api/bookmarks')
assert any(b['id'] == target_id for b in r_list.json()['bookmarks'])
print('Bookmark ON verified for Job ID:', target_id)

# Toggle OFF
r_bm_off = requests.post(base_url + f'/api/bookmark/{target_id}')
assert r_bm_off.status_code == 200
assert r_bm_off.json()['is_bookmarked'] is False
print('Bookmark OFF toggle lifecycle verified.')

print('\n--- CHECK 14: CSV Export ---')
r = requests.get(base_url + '/api/export')
print('CSV Status:', r.status_code, 'Content-Type:', r.headers.get('Content-Type'), 'Bytes:', len(r.content))
assert r.status_code == 200 and 'text/csv' in r.headers.get('Content-Type')
assert 'Title (EN)' in r.text and 'OJAS' in r.text

print('\n--- CHECK 15: Job Alert Subscription ---')
r_sub = requests.post(base_url + '/api/subscribe', json={
    'name': 'Deep Reviewer',
    'email': 'deep.reviewer@futurset.test',
    'state_pref': 'Gujarat',
    'preferred_boards': ['OJAS', 'GPSC', 'Police']
})
print('Subscribe Status:', r_sub.status_code, r_sub.json())
assert r_sub.status_code == 200
assert r_sub.json()['status'] == 'success'

print('\n--- CHECK 16: Sector Filtering API ---')
for sec in ['police', 'civil', 'clerk', 'engineering', 'teaching', 'medical', 'railways', 'banking', 'transport', 'electricity', 'forest']:
    r = requests.get(base_url + f'/api/jobs?sector={sec}')
    assert r.status_code == 200
    sec_data = r.json()
    print(f' - Sector [{sec}]: {sec_data["count"]} jobs found')
    assert sec_data['count'] > 0, f"Sector {sec} must return matching jobs"

print('\n--- CHECK 17: Urgency & Fee Filtering API ---')
r_week = requests.get(base_url + '/api/jobs?urgency=closing_week')
assert r_week.status_code == 200
print('Closing this week:', r_week.json()['count'])

r_fee = requests.get(base_url + '/api/jobs?urgency=no_fee')
assert r_fee.status_code == 200
print('Fee exempted (Rs 0):', r_fee.json()['count'])
assert r_fee.json()['count'] > 0

print('\n--- CHECK 18: Qualification Filtering API ---')
for q in ['10th', '12th', 'Diploma', 'Graduate', 'Engineering']:
    r = requests.get(base_url + f'/api/jobs?qualification={q}')
    assert r.status_code == 200
    q_data = r.json()
    print(f' - Qual [{q}]: {q_data["count"]} jobs found')
    assert q_data['count'] > 0

print('\n--- CHECK 19: District Filtering API for Gujarat ---')
r_dist = requests.get(base_url + '/api/jobs?state=Gujarat&district=ગાંધીનગર')
assert r_dist.status_code == 200
print('Gandhinagar district jobs:', r_dist.json()['count'])

print('\n--- CHECK 20: Scale Verification (600,000+ Vacancies & 100+ Jobs) ---')
r_stats = requests.get(base_url + '/api/stats').json()
print(f'Total Jobs: {r_stats["total_jobs"]}, Total Vacancies: {r_stats["total_vacancies"]:,}')
print(f'Gujarat Posts: {r_stats["gujarat_vacancies"]:,}, Central Posts: {r_stats["central_vacancies"]:,}')
assert r_stats['total_jobs'] >= 100, "Must have over 100 authentic recruitments"
assert r_stats['total_vacancies'] >= 600000, "Must aggregate over 600,000 active vacancies"
assert r_stats['gujarat_vacancies'] >= 100000, "Must have over 100,000 Gujarat posts"
assert r_stats['central_vacancies'] >= 400000, "Must have over 400,000 Central posts"

print('\n>>> ALL 20 DEEP LIVE VERIFICATION CHECKS PASSED WITH 100% SUCCESS! <<<')
