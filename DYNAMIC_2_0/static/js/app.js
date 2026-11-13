document.addEventListener('click',e=>{if(e.target.closest('.app-main')&&document.body.classList.contains('nav-open')&&innerWidth<760)document.body.classList.remove('nav-open')});


// Attach the server-issued CSRF token to standard forms and same-origin fetch requests.
(() => {
  const token = document.querySelector('meta[name="csrf-token"]')?.content;
  if (!token) return;

  const addTokenToForms = () => {
    document.querySelectorAll('form[method="post"], form[method="POST"], form[method="put"], form[method="delete"]').forEach(form => {
      if (!form.querySelector('input[name="_csrf_token"]')) {
        const field = document.createElement('input');
        field.type = 'hidden';
        field.name = '_csrf_token';
        field.value = token;
        form.appendChild(field);
      }
    });
  };

  addTokenToForms();
  document.addEventListener('DOMContentLoaded', addTokenToForms);

  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init = {}) => {
    const method = (init.method || (input instanceof Request ? input.method : 'GET')).toUpperCase();
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
      const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined));
      headers.set('X-CSRFToken', token);
      init = { ...init, headers };
    }
    return nativeFetch(input, init);
  };
})();
