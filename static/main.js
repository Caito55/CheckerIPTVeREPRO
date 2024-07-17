document.addEventListener('DOMContentLoaded', (event) => {
    const socket = io.connect('http://' + document.domain + ':' + location.port);

    const form = document.getElementById('m3u-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const m3uUrl = document.getElementById('m3u_url').value;
        socket.emit('check_channels', {m3u_url: m3uUrl});
        
        document.getElementById('progress-container').style.display = 'block';
        document.getElementById('working-channels-container').style.display = 'none';
        document.getElementById('failed-channels-container').style.display = 'none';
    });

    socket.on('progress', function(data) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        progressBar.value = data.progress;
        progressText.textContent = data.progress.toFixed(2) + '%';
    });

    socket.on('channels', function(data) {
        const workingChannelsList = document.getElementById('working-channels-list');
        workingChannelsList.innerHTML = '';

        data.working_channels.forEach(channel => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <strong>${channel.name}</strong>
                <br>
                <video controls width="600">
                    <source src="${channel.url}" type="application/x-mpegURL">
                    Your browser does not support the video tag.
                </video>
            `;
            workingChannelsList.appendChild(listItem);
        });

        const failedChannelsList = document.getElementById('failed-channels-list');
        failedChannelsList.innerHTML = '';

        data.failed_channels.forEach(channel => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <strong>${channel.name}</strong> - Error: ${channel.error}
            `;
            failedChannelsList.appendChild(listItem);
        });

        document.getElementById('progress-container').style.display = 'none';
        document.getElementById('working-channels-container').style.display = 'block';
        document.getElementById('failed-channels-container').style.display = 'block';
    });
});
