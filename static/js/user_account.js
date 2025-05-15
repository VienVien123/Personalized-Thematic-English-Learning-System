document.addEventListener('DOMContentLoaded', () => {
    const user = JSON.parse(localStorage.getItem('user'));
  
    function formatDateToInput(value) {
      if (!value) return '';
      const parts = value.split('/');
      if (parts.length === 3) {
        return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
      }
      return value;
    }
  
    if (user) {
      document.getElementById('username').value = user.email;
      document.getElementById('email').value = user.email;
      document.getElementById('name').value = user.name;
      document.getElementById('birthday').value = formatDateToInput(user.birthday);
      document.getElementById('gender').value = user.gender || 'Nam';
      document.getElementById('city').value = user.city || '';
      document.getElementById('district').value = user.district || '';
      document.getElementById('ward').value = user.ward || '';
      document.getElementById('street').value = user.street || '';
      document.getElementById('company').value = user.company || '';
      document.getElementById('position').value = user.position || '';
      document.getElementById('university').value = user.university || '';
      document.getElementById('major').value = user.major || '';
      document.getElementById('phone').value = user.phone || '';
      document.getElementById('facebook').value = user.facebook || '';
      document.getElementById('bio').value = user.bio || '';
  
      const preview = document.getElementById('avatar-preview');
      const baseUrl = window.location.origin;
      if (user.avatar) {
        preview.src = user.avatar;
      } else {
        preview.src = '/static/img/default-avatar.png';
      }
    }
  
    document.getElementById('avatar').addEventListener('change', function (e) {
      const file = e.target.files[0];
      const preview = document.getElementById('avatar-preview');
  
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          preview.src = event.target.result;
        };
        reader.readAsDataURL(file);
      }
    });
  
    document.getElementById('account-info-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const token = localStorage.getItem('access');
  
      const formData = new FormData();
      formData.append('email', document.getElementById('email').value);
      formData.append('name', document.getElementById('name').value);
      formData.append('birthday', document.getElementById('birthday').value);
      formData.append('gender', document.getElementById('gender').value);
      formData.append('city', document.getElementById('city').value);
      formData.append('district', document.getElementById('district').value);
      formData.append('ward', document.getElementById('ward').value);
      formData.append('street', document.getElementById('street').value);
      formData.append('company', document.getElementById('company').value);
      formData.append('position', document.getElementById('position').value);
      formData.append('university', document.getElementById('university').value);
      formData.append('major', document.getElementById('major').value);
      formData.append('phone', document.getElementById('phone').value);
      formData.append('facebook', document.getElementById('facebook').value);
      formData.append('bio', document.getElementById('bio').value);
  
      const avatarFile = document.getElementById('avatar').files[0];
      if (avatarFile) formData.append('avatar', avatarFile);
  
      const res = await fetch('/api/user/account/', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
  
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('user', JSON.stringify(data));
        loadUserAvatar();  // header cập nhật lại avatar từ user.avatar
        alert('Cập nhật thông tin thành công!');
      } else {
        const firstKey = Object.keys(data)[0];
        alert(data[firstKey][0]);
      }
    });
});