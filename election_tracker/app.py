import csv
import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'exam_secret_key'

# ==========================================
#  MODEL LAYER (จัดการ CSV)
# ==========================================
DB_FOLDER = 'database'

class BaseModel:
    def __init__(self, filename, fieldnames):
        self.filepath = os.path.join(DB_FOLDER, filename)
        self.fieldnames = fieldnames
        self.ensure_file_exists()

    def ensure_file_exists(self):
        if not os.path.exists(DB_FOLDER):
            os.makedirs(DB_FOLDER)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def get_all(self):
        data = []
        with open(self.filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

    def add(self, item):
        with open(self.filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(item)

    def update_record(self, id_field, id_value, update_data):
        rows = self.get_all()
        updated_rows = []
        for row in rows:
            if row[id_field] == id_value:
                row.update(update_data)
            updated_rows.append(row)
        
        with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)

# --- Define Models ---
class PoliticianModel(BaseModel):
    def __init__(self):
        super().__init__('politicians.csv', ['id', 'name', 'party'])
    def get_by_id(self, pid):
        for p in self.get_all():
            if p['id'] == pid: return p
        return None

class CampaignModel(BaseModel):
    def __init__(self):
        super().__init__('campaigns.csv', ['id', 'politician_id', 'year', 'constituency'])
    def get_by_politician_id(self, pid):
        for c in self.get_all():
            if c['politician_id'] == pid: return c
        return None

class PromiseModel(BaseModel):
    def __init__(self):
        super().__init__('promises.csv', ['id', 'politician_id', 'detail', 'date', 'status'])
    def get_by_id(self, pid):
        for p in self.get_all():
            if p['id'] == pid: return p
        return None
    def get_by_politician(self, pol_id):
        return [p for p in self.get_all() if p['politician_id'] == pol_id]
    def get_all_sorted(self):
        return sorted(self.get_all(), key=lambda x: x['date'], reverse=True)

class UpdateModel(BaseModel):
    def __init__(self):
        super().__init__('promise_updates.csv', ['promise_id', 'date', 'detail'])
    def get_by_promise(self, promise_id):
        return sorted([u for u in self.get_all() if u['promise_id'] == promise_id], key=lambda x: x['date'], reverse=True)

# Init Models
politician_model = PoliticianModel()
campaign_model = CampaignModel()
promise_model = PromiseModel()
update_model = UpdateModel()

# --- SEED DATA (อัปเดตใหม่: เพิ่มคนและคำสัญญา) ---
def seed_data():
    if not politician_model.get_all():
        print("Seeding Data...")
        
        pols = [
            {'id': '10000001', 'name': 'นาย ก.', 'party': 'พรรคใจมั่น'},
            {'id': '10000002', 'name': 'นาง ข.', 'party': 'พรรคใจมั่น'},
            {'id': '10000003', 'name': 'นาย ค.', 'party': 'พรรคก้าวหน้า'},
            {'id': '10000004', 'name': 'นาง ง.', 'party': 'พรรคก้าวหน้า'},
            {'id': '10000005', 'name': 'นาย จ.', 'party': 'พรรคอิสระ'},
            {'id': '10000006', 'name': 'นาย ฉ.', 'party': 'พรรคใจมั่น'},   # เพิ่มให้พรรคใจมั่น
            {'id': '10000007', 'name': 'นาง ช.', 'party': 'พรรคก้าวหน้า'}, # เพิ่มให้พรรคก้าวหน้า
            {'id': '10000008', 'name': 'นาย ซ.', 'party': 'พรรคพลังใหม่'}, # พรรคใหม่
            {'id': '10000009', 'name': 'นาง ฌ.', 'party': 'พรรคพลังใหม่'}, # พรรคใหม่
            {'id': '10000010', 'name': 'นาย ญ.', 'party': 'พรรคอิสระ'}     # เพิ่มให้พรรคอิสระ
        ]
        for p in pols: politician_model.add(p)


        camps = [
            {'id': 'C01', 'politician_id': '10000001', 'year': '2566', 'constituency': 'กทม. เขต 1'},
            {'id': 'C02', 'politician_id': '10000002', 'year': '2566', 'constituency': 'กทม. เขต 2'},
            {'id': 'C03', 'politician_id': '10000003', 'year': '2566', 'constituency': 'เชียงใหม่ เขต 1'},
            {'id': 'C04', 'politician_id': '10000004', 'year': '2566', 'constituency': 'เชียงใหม่ เขต 2'},
            {'id': 'C05', 'politician_id': '10000005', 'year': '2566', 'constituency': 'ชลบุรี เขต 1'},
            {'id': 'C06', 'politician_id': '10000006', 'year': '2566', 'constituency': 'กทม. เขต 3'},
            {'id': 'C07', 'politician_id': '10000007', 'year': '2566', 'constituency': 'ขอนแก่น เขต 1'},
            {'id': 'C08', 'politician_id': '10000008', 'year': '2566', 'constituency': 'นครราชสีมา เขต 1'},
            {'id': 'C09', 'politician_id': '10000009', 'year': '2566', 'constituency': 'นครราชสีมา เขต 2'},
            {'id': 'C10', 'politician_id': '10000010', 'year': '2566', 'constituency': 'ภูเก็ต เขต 1'}
        ]
        for c in camps: campaign_model.add(c)

        # 3. คำสัญญา (เพิ่มอีก 5 เป็น 15 ข้อ)
        proms = [
            # ของเดิม 10 ข้อ
            {'id': '1', 'politician_id': '10000001', 'detail': 'รถเมล์ไฟฟ้าทั่วกรุง', 'date': '2025-01-10', 'status': 'กำลังดำเนินการ'},
            {'id': '2', 'politician_id': '10000001', 'detail': 'ลดค่าครองชีพ', 'date': '2025-01-12', 'status': 'เงียบหาย'},
            {'id': '3', 'politician_id': '10000002', 'detail': 'สวนสาธารณะทุกเขต', 'date': '2025-02-01', 'status': 'ยังไม่เริ่ม'},
            {'id': '4', 'politician_id': '10000002', 'detail': 'ทางเท้าดีทั่วกรุง', 'date': '2025-02-05', 'status': 'กำลังดำเนินการ'},
            {'id': '5', 'politician_id': '10000003', 'detail': 'แก้ฝุ่น PM2.5 เชียงใหม่', 'date': '2025-01-20', 'status': 'เงียบหาย'},
            {'id': '6', 'politician_id': '10000003', 'detail': 'ตลาดนัดชุมชน', 'date': '2025-01-25', 'status': 'ยังไม่เริ่ม'},
            {'id': '7', 'politician_id': '10000004', 'detail': 'ส่งเสริมท่องเที่ยวเมืองเหนือ', 'date': '2025-02-10', 'status': 'กำลังดำเนินการ'},
            {'id': '8', 'politician_id': '10000004', 'detail': 'ศูนย์เรียนรู้เยาวชน', 'date': '2025-02-15', 'status': 'กำลังดำเนินการ'},
            {'id': '9', 'politician_id': '10000005', 'detail': 'ประกันราคาพืชผล', 'date': '2025-03-01', 'status': 'ยังไม่เริ่ม'},
            {'id': '10', 'politician_id': '10000005', 'detail': 'ประมงยั่งยืน', 'date': '2025-03-05', 'status': 'ยังไม่เริ่ม'},

            {'id': '11', 'politician_id': '10000006', 'detail': 'เพิ่มกล้องวงจรปิดทั่วกรุง', 'date': '2025-03-10', 'status': 'ยังไม่เริ่ม'},
            {'id': '12', 'politician_id': '10000007', 'detail': 'กองทุนหมู่บ้านเพิ่มทุน', 'date': '2025-03-12', 'status': 'กำลังดำเนินการ'},
            {'id': '13', 'politician_id': '10000008', 'detail': 'รถไฟความเร็วสูงโคราช', 'date': '2025-03-15', 'status': 'ยังไม่เริ่ม'},
            {'id': '14', 'politician_id': '10000009', 'detail': 'แก้ปัญหาน้ำแล้งอีสาน', 'date': '2025-03-18', 'status': 'เงียบหาย'},
            {'id': '15', 'politician_id': '10000010', 'detail': 'ภูเก็ตเมืองท่องเที่ยวระดับโลก', 'date': '2025-03-20', 'status': 'กำลังดำเนินการ'}
        ]
        for pr in proms: promise_model.add(pr)

seed_data()


#  CONTROLLER LAYER (Routes)

@app.route('/')
def index():
    promises = promise_model.get_all_sorted()
    for p in promises:
        pol = politician_model.get_by_id(p['politician_id'])
        p['politician_name'] = pol['name'] if pol else 'Unknown'
        p['politician_party'] = pol['party'] if pol else '-'
    return render_template('index.html', promises=promises)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u == 'admin' and p == '1234':
            session['role'] = 'admin'
            session['username'] = 'Admin'
            return redirect(url_for('index'))
        elif u == 'user' and p == '1234':
            session['role'] = 'user'
            session['username'] = 'User'
            return redirect(url_for('index'))
        else:
            flash('Login Failed')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/promise/<pid>')
def promise_detail(pid):
    promise = promise_model.get_by_id(pid)
    if not promise: return "Not Found", 404
    pol = politician_model.get_by_id(promise['politician_id'])
    camp = campaign_model.get_by_politician_id(pol['id'])
    updates = update_model.get_by_promise(pid)
    return render_template('detail.html', promise=promise, politician=pol, campaign=camp, updates=updates)

@app.route('/politician/<pid>')
def politician_detail(pid):
    pol = politician_model.get_by_id(pid)
    if not pol: return "Not Found", 404
    camp = campaign_model.get_by_politician_id(pid)
    promises = promise_model.get_by_politician(pid)
    return render_template('politician.html', politician=pol, campaign=camp, promises=promises)

@app.route('/parties')
def party_view():
    pols = politician_model.get_all()
    parties_data = {}
    for p in pols:
        party_name = p['party']
        if party_name not in parties_data: parties_data[party_name] = []
        p['my_promises'] = promise_model.get_by_politician(p['id'])
        parties_data[party_name].append(p)
    sorted_parties = dict(sorted(parties_data.items()))
    return render_template('parties.html', parties=sorted_parties)

@app.route('/add_promise', methods=['GET', 'POST'])
def add_promise():
    if session.get('role') != 'admin':
        flash('Admin Only')
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Simple ID generation
        all_ids = [int(p['id']) for p in promise_model.get_all()]
        new_id = str(max(all_ids) + 1) if all_ids else '1'
        
        promise_model.add({
            'id': new_id,
            'politician_id': request.form['politician_id'],
            'detail': request.form['detail'],
            'date': request.form['date'],
            'status': 'ยังไม่เริ่ม'
        })
        flash('เพิ่มข้อมูลสำเร็จ')
        return redirect(url_for('index'))
    return render_template('add_promise.html', politicians=politician_model.get_all())

@app.route('/update/<pid>', methods=['GET', 'POST'])
def update_promise(pid):
    if session.get('role') != 'admin':
        flash('Admin Only')
        return redirect(url_for('promise_detail', pid=pid))
    promise = promise_model.get_by_id(pid)
    if promise['status'] == 'เงียบหาย':
        flash('ไม่สามารถแก้ไขสถานะ เงียบหาย ได้')
        return redirect(url_for('promise_detail', pid=pid))
    
    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status and new_status != promise['status']:
            promise_model.update_record('id', pid, {'status': new_status})
        detail = request.form.get('detail')
        if detail:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_model.add({'promise_id': pid, 'date': now, 'detail': detail})
        return redirect(url_for('promise_detail', pid=pid))
    return render_template('update.html', promise=promise)

if __name__ == '__main__':
    app.run(debug=True)