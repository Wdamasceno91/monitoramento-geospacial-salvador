import pandas as pd
import folium
import os
import webbrowser
from folium.plugins import HeatMap, Fullscreen

# 1. Carregamento dos dados
file_path = 'dados_seguranca_2026.csv'

if not os.path.exists(file_path):
    print(f"Erro: Arquivo {file_path} nao encontrado.")
else:
    df = pd.read_csv(file_path)

    # 2. Criacao do Mapa Base
    mapa = folium.Map(
        location=[-12.9880, -38.5180],
        zoom_start=14,
        tiles='cartodbdark_matter'
    )

    # 3. Painel Lateral (Card Dinamico)
    painel_html = f"""
    <div id="info-card" style="
        position: fixed; top: 20px; left: 20px; width: 300px;
        z-index:9999; background-color: rgba(5, 10, 20, 0.95);
        color: white; padding: 25px; border-radius: 4px;
        font-family: 'Segoe UI', sans-serif; border-left: 5px solid #00aaff;
        box-shadow: 10px 10px 30px rgba(0,0,0,0.5);
        pointer-events: none;
    ">
        <div style="color: #00aaff; font-size: 10px; font-weight: bold; letter-spacing: 2px;">MONITORAMENTO GEOGRÁFICO</div>
        <h2 id="v_nome" style="margin: 10px 0 20px 0; font-size: 18px; font-weight: 400;">Salvador (Geral)</h2>
        <hr style="border: 0.1px solid #1a3a5a; margin-bottom: 20px;">
        
        <div style="margin-bottom: 15px;">
            <div style="font-size: 10px; color: #666;">CRIME PRINCIPAL</div>
            <div id="v_crime" style="font-size: 16px; font-weight: bold; color: #ff4d4d;">---</div>
        </div>

        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <div>
                <div style="font-size: 10px; color: #666;">ROUBOS</div>
                <div id="v_roubos" style="font-size: 26px; font-weight: bold; color: #ff4d4d;">{df['Roubos'].sum()}</div>
            </div>
            <div>
                <div style="font-size: 10px; color: #666;">FURTOS</div>
                <div id="v_furtos" style="font-size: 26px; font-weight: bold;">{df['Furtos'].sum()}</div>
            </div>
        </div>
        
        <div style="margin-bottom: 5px;">
            <div style="font-size: 10px; color: #666;">EFETIVO POLICIAL</div>
            <div id="v_efetivo" style="font-size: 20px; font-weight: bold;">{df['Efetivo'].sum()}</div>
        </div>
    </div>

    <script>
    function hoverData(nome, crime, roubos, furtos, efetivo) {{
        document.getElementById('v_nome').innerText = nome;
        document.getElementById('v_crime').innerText = crime;
        document.getElementById('v_roubos').innerText = roubos;
        document.getElementById('v_furtos').innerText = furtos;
        document.getElementById('v_efetivo').innerText = efetivo;
        
        document.getElementById('info-card').style.borderLeftColor = '#ff4d4d';
    }}
    
    function resetData() {{
        // Opcional: Voltar ao total geral ao tirar o mouse
    }}
    </script>
    """
    mapa.get_root().html.add_child(folium.Element(painel_html))

    # 4. Camada de Calor
    heat_data = [[row['Lat'], row['Lon'], row['Roubos']] for i, row in df.iterrows()]
    HeatMap(heat_data, radius=35, blur=25, min_opacity=0.3, 
            gradient={0.4: 'blue', 0.7: 'cyan', 1: 'red'}).add_to(mapa)

    # 5. Sensores de Mouse (Hover Invisível)
    for i, row in df.iterrows():
        # Sensor invisível
        sensor = folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=40,
            color='transparent',
            fill=True,
            fill_opacity=0,
            tooltip=folium.Tooltip(f"<b>{row['Circuito']}</b><br>Roubos: {row['Roubos']}", sticky=False)
        )

        # Injeção de JS para o evento OnMouseOver (Passar o mouse)
        js_hover = f"hoverData('{row['Circuito']}', '{row['Crime_Principal']}', {row['Roubos']}, {row['Furtos']}, {row['Efetivo']})"
        
        sensor.add_child(folium.Element(f"""
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    var items = document.getElementsByClassName('leaflet-interactive');
                    var target = items[items.length - 1];
                    if (target) {{
                        target.onmouseover = function() {{ {js_hover} }};
                    }}
                }});
            </script>
        """))
        sensor.add_to(mapa)

    # 6. Finalização
    Fullscreen().add_to(mapa)
    arquivo_final = "mapa_seguranca_hover.html"
    mapa.save(arquivo_final)

    webbrowser.open(f"file:///{os.path.abspath(arquivo_final).replace(os.sep, '/')}")
    print("Dashboard interativo por aproximação gerado.")