Name:           sistema-etiquetas
Version:        4.0
Release:        1%{?dist}
Summary:        Sistema de impresión de etiquetas con integración Odoo

License:        MIT
URL:            https://github.com/your-org/sistema-etiquetas
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python3

%description
Sistema de impresión de etiquetas que permite:
- Búsqueda de productos en sistemas Odoo
- Generación de etiquetas ZPL
- Impresión directa a impresoras de red
- Registro de impresiones en base de datos MySQL
- Interfaz gráfica moderna con PyQt6

%prep
%autosetup

%build
# No build step needed for Python application

%install
# Crear directorio de instalación
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_datadir}/applications

# Copiar ejecutable
cp dist/SistemaEtiquetas %{buildroot}%{_bindir}/sistema-etiquetas
chmod +x %{buildroot}%{_bindir}/sistema-etiquetas

# Copiar archivos de datos
cp styles.qss %{buildroot}%{_datadir}/%{name}/ 2>/dev/null || true
cp odoo_config.py %{buildroot}%{_datadir}/%{name}/ 2>/dev/null || true
cp printer_config.json %{buildroot}%{_datadir}/%{name}/ 2>/dev/null || true
cp src/assets/icon.ico %{buildroot}%{_datadir}/%{name}/ 2>/dev/null || true

# Crear archivo .desktop
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Sistema de Etiquetas
Comment=Sistema de impresión de etiquetas con integración Odoo
Exec=sistema-etiquetas
Icon=%{_datadir}/%{name}/icon.ico
Terminal=false
Categories=Office;
EOF

%files
%license LICENSE
%doc README_FEDORA.md
%{_bindir}/sistema-etiquetas
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop

%changelog
* Sun Aug 04 2024 Your Name <your.email@example.com> - 4.0-1
- Initial RPM package for Fedora
- Single executable with all dependencies included
- Desktop integration with menu entry 