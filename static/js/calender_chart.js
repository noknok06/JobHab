document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ja',
        events: '/project_management/tickets/events/',  // イベントデータの取得URL
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,listMonth'
        },
        eventClick: function (info) {
            info.jsEvent.preventDefault(); // 既定のクリック動作を防止
            if (info.event.url) {
                window.open(info.event.url, '_blank');
            }
        },
        eventMouseEnter: function (info) {  // ホバーでツールチップ表示
            var tooltip = document.createElement('div');
            tooltip.innerText = info.event.extendedProps.detail || '詳細なし';
            tooltip.classList.add('event-tooltip');
            document.body.appendChild(tooltip);
            tooltip.style.top = (info.jsEvent.pageY + 10) + 'px';
            tooltip.style.left = (info.jsEvent.pageX + 10) + 'px';
        },
        eventMouseLeave: function () {  // ツールチップを消去
            var tooltip = document.querySelector('.event-tooltip');
            if (tooltip) tooltip.remove();
        },
        eventDidMount: function (info) {  // プロジェクトごとに動的な色を適用
            var projectColor = info.event.extendedProps.project_color;
            if (projectColor) {
                info.el.style.backgroundColor = projectColor;
            }
        },
    });
    calendar.render();
});