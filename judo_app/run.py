# Copyright (c) 2025 Dimitri Lefebvre
# Tous droits réservés. Ce fichier fait partie d'un logiciel propriétaire.
# Son utilisation est soumise aux conditions définies dans le fichier LICENSE.

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0', port=80)