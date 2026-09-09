describe('Pruebas de Integración de API - Ferretería El Martillo', () => {
    const baseUrl = 'http://127.0.0.1:8000/api/v1';
    let authToken = '';
    let productoId = null;

    before(() => {
        cy.env(['API_USERNAME', 'API_PASSWORD']).then((credentials) => {
            cy.request({
                method: 'POST',
                url: `${baseUrl}/auth/token/`,
                body: {
                    username: credentials.API_USERNAME || 'Jose',
                    password: credentials.API_PASSWORD || 'Juliana21'
                }
            }).then((response) => {
                expect(response.status).to.eq(200);
                expect(response.body).to.have.property('token');
                authToken = response.body.token;
            });
        });
    });

    it('1. POST - Crear un nuevo producto con Token en Authorization', () => {
        cy.request({
            method: 'POST',
            url: `${baseUrl}/productos/`,
            headers: {
                Authorization: `Token ${authToken}`
            },
            body: {
                nombre: 'Esmeril Angular 4-1/2',
                codigo: 'FERR-888',
                precio_base: 210000.00,
                stock: 12
            }
        }).then((response) => {
            expect(response.status).to.eq(201);
            expect(response.body).to.have.property('id');
            expect(response.body.precio_final).to.eq(249900.00); // 210000 * 1.19
            productoId = response.body.id;
        });
    });

    // Paso 3: Consultar y Verificar Persistencia
    it('3. GET - Consultar el producto creado por ID', () => {
        cy.request({
            method: 'GET',
            url: `${baseUrl}/productos/${productoId}/`
        }).then((response) => {
            expect(response.status).to.eq(200);
            expect(response.body.nombre).to.eq('Esmeril Angular 4-1/2');
        });
    });

    // Paso 4: Eliminar Recurso
    it('4. DELETE - Eliminar el producto y verificar 204 No Content', () => {
        cy.request({
            method: 'DELETE',
            url: `${baseUrl}/productos/${productoId}/`,
            headers: {
                Authorization: `Token ${authToken}`
            }
        }).then((response) => {
            expect(response.status).to.eq(204);
        });
    });
});