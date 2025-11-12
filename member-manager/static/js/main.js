/**
 * Member Manager モックアップ用JavaScript
 * 将来的にはVue.jsやReactなどのフレームワークへの移行を検討
 * 現在はバニラJavaScriptで実装
 */

let currentTable = null;
let currentData = [];
let currentColumns = [];
let editingRecord = null;
let deletingRecord = null;

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    const tableSelect = document.getElementById('tableSelect');
    tableSelect.addEventListener('change', handleTableChange);

    document.getElementById('addRecordBtn').addEventListener('click', handleAddRecord);
});

/**
 * テーブル選択時の処理
 * 将来的にはデータベースから直接データを取得
 */
async function handleTableChange(event) {
    const tableName = event.target.value;

    if (!tableName) {
        document.getElementById('dataSection').style.display = 'none';
        return;
    }

    currentTable = tableName;

    try {
        const response = await fetch(`/api/table/${tableName}`);
        const data = await response.json();

        if (response.ok) {
            currentColumns = data.columns;
            currentData = data.data;
            displayTable(tableName, data.columns, data.data);
        } else {
            alert('データの取得に失敗しました: ' + data.error);
        }
    } catch (error) {
        console.error('Error fetching table data:', error);
        alert('データの取得中にエラーが発生しました');
    }
}

/**
 * テーブルデータを表示
 * 将来的にはJinjaテンプレートでサーバーサイドレンダリング
 */
function displayTable(tableName, columns, data) {
    document.getElementById('tableName').textContent = tableName;
    document.getElementById('dataSection').style.display = 'block';

    // ヘッダーを作成
    const tableHead = document.getElementById('tableHead');
    tableHead.innerHTML = '';
    const headerRow = document.createElement('tr');

    columns.forEach(column => {
        const th = document.createElement('th');
        th.textContent = column;
        headerRow.appendChild(th);
    });

    // アクション列を追加
    const actionTh = document.createElement('th');
    actionTh.textContent = 'アクション';
    actionTh.className = 'action-column';
    headerRow.appendChild(actionTh);

    tableHead.appendChild(headerRow);

    // ボディを作成
    const tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = '';

    data.forEach((record, index) => {
        const row = document.createElement('tr');

        columns.forEach(column => {
            const td = document.createElement('td');
            const value = record[column];

            // UUIDなど長い値は省略表示
            if (typeof value === 'string' && value.length > 20) {
                td.textContent = value.substring(0, 20) + '...';
                td.title = value;
            } else {
                td.textContent = value || '';
            }

            row.appendChild(td);
        });

        // アクションボタンを追加
        const actionTd = document.createElement('td');
        actionTd.className = 'action-column';
        actionTd.innerHTML = `
            <button class="btn btn-sm btn-edit" onclick="editRecord(${index})">編集</button>
            <button class="btn btn-sm btn-delete" onclick="deleteRecord(${index})">削除</button>
        `;
        row.appendChild(actionTd);

        tableBody.appendChild(row);
    });
}

/**
 * 新規レコード追加
 * 将来的にはフォームバリデーションを強化
 */
function handleAddRecord() {
    editingRecord = null;
    document.getElementById('modalTitle').textContent = '新規レコード追加';
    showEditModal({});
}

/**
 * レコード編集
 */
function editRecord(index) {
    editingRecord = currentData[index];
    document.getElementById('modalTitle').textContent = 'レコード編集';
    showEditModal(editingRecord);
}

/**
 * 編集モーダルを表示
 */
function showEditModal(record) {
    const form = document.getElementById('editForm');
    form.innerHTML = '';

    currentColumns.forEach(column => {
        // 自動生成される項目はスキップ
        if (column === 'created_at' || column === 'updated_at') {
            return;
        }

        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';

        const label = document.createElement('label');
        label.textContent = column;
        label.setAttribute('for', column);

        const input = document.createElement('input');
        input.type = 'text';
        input.id = column;
        input.name = column;
        input.className = 'form-control';
        input.value = record[column] || '';

        // IDフィールドは編集時は読み取り専用
        if ((column.endsWith('_id') || column.endsWith('_uuid')) && editingRecord) {
            input.readOnly = true;
        }

        formGroup.appendChild(label);
        formGroup.appendChild(input);
        form.appendChild(formGroup);
    });

    document.getElementById('editModal').style.display = 'block';
}

/**
 * モーダルを閉じる
 */
function closeModal() {
    document.getElementById('editModal').style.display = 'none';
    editingRecord = null;
}

/**
 * レコードを保存
 * 将来的にはデータベースに直接保存
 */
async function saveRecord() {
    const form = document.getElementById('editForm');
    const formData = new FormData(form);
    const record = {};

    for (let [key, value] of formData.entries()) {
        record[key] = value;
    }

    try {
        let response;
        if (editingRecord) {
            // 更新
            const idField = getIdField();
            const recordId = editingRecord[idField];
            response = await fetch(`/api/table/${currentTable}/record/${recordId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(record)
            });
        } else {
            // 新規作成
            response = await fetch(`/api/table/${currentTable}/record`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(record)
            });
        }

        const data = await response.json();

        if (response.ok) {
            alert('保存しました');
            closeModal();
            // テーブルを再読み込み
            document.getElementById('tableSelect').dispatchEvent(new Event('change'));
        } else {
            alert('保存に失敗しました: ' + data.error);
        }
    } catch (error) {
        console.error('Error saving record:', error);
        alert('保存中にエラーが発生しました');
    }
}

/**
 * レコード削除
 */
function deleteRecord(index) {
    deletingRecord = currentData[index];
    const info = document.getElementById('deleteInfo');
    info.textContent = JSON.stringify(deletingRecord, null, 2);
    document.getElementById('deleteModal').style.display = 'block';
}

/**
 * 削除モーダルを閉じる
 */
function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    deletingRecord = null;
}

/**
 * 削除を確定
 * 将来的にはデータベースから直接削除
 */
async function confirmDelete() {
    if (!deletingRecord) return;

    try {
        const idField = getIdField();
        const recordId = deletingRecord[idField];

        const response = await fetch(`/api/table/${currentTable}/record/${recordId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            alert('削除しました');
            closeDeleteModal();
            // テーブルを再読み込み
            document.getElementById('tableSelect').dispatchEvent(new Event('change'));
        } else {
            alert('削除に失敗しました: ' + data.error);
        }
    } catch (error) {
        console.error('Error deleting record:', error);
        alert('削除中にエラーが発生しました');
    }
}

/**
 * 現在のテーブルのIDフィールドを取得
 */
function getIdField() {
    if (currentTable.includes('profile')) {
        return 'profile_id';
    } else if (currentTable.includes('relationship')) {
        return 'relationship_id';
    } else {
        return 'member_id';
    }
}
