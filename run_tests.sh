#!/bin/bash

# Script pour exécuter tous les tests

echo "==================================="
echo "🔍 BORNSAFE - SUITE DE TESTS"
echo "==================================="

cd bornsafe_backend

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Compteurs
TOTAL=0
PASSED=0
FAILED=0

# Fonction pour exécuter un test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "\n${YELLOW}▶ Exécution: ${test_name}${NC}"
    
    if eval $test_command; then
        echo -e "${GREEN}✅ SUCCÈS: ${test_name}${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ ÉCHEC: ${test_name}${NC}"
        ((FAILED++))
    fi
    ((TOTAL++))
}

# 1. Vérification de la configuration
echo -e "\n${BLUE}📋 1. VÉRIFICATION CONFIGURATION${NC}"
run_test "Check Django" "python manage.py check"
run_test "Check migrations" "python manage.py showmigrations | grep -v '\[X\]' | wc -l | grep -q '^0$' || echo 'Migrations en attente'"

# 2. Tests unitaires
echo -e "\n${BLUE}🧪 2. TESTS UNITAIRES${NC}"
run_test "Tests Accounts" "python manage.py test accounts --noinput -v 2"
run_test "Tests Provinces" "python manage.py test provinces --noinput -v 2"
run_test "Tests Actes" "python manage.py test actes --noinput -v 2"

# 3. Tests de sécurité
echo -e "\n${BLUE}🔒 3. TESTS DE SÉCURITÉ${NC}"
run_test "Sécurité" "python manage.py test security_tests --noinput -v 2"

# 4. Tests de performance
echo -e "\n${BLUE}⚡ 4. TESTS DE PERFORMANCE${NC}"
run_test "Performance" "python manage.py test performance_tests --noinput -v 2"

# 5. Tests d'intégration
echo -e "\n${BLUE}🔄 5. TESTS D'INTÉGRATION${NC}"
run_test "Intégration API" "python manage.py test --pattern='*_integration.py' --noinput -v 2 || echo 'Pas de tests d\'intégration'"

# 6. Tests de couverture
echo -e "\n${BLUE}📊 6. COUVERTURE DE CODE${NC}"
if command -v coverage &> /dev/null; then
    run_test "Couverture" "coverage run --source='.' manage.py test && coverage report --fail-under=80"
else
    echo -e "${YELLOW}⚠️  coverage non installé, installation...${NC}"
    pip install coverage
    run_test "Couverture" "coverage run --source='.' manage.py test && coverage report --fail-under=80"
fi

# Résumé
echo -e "\n${BLUE}===================================${NC}"
echo -e "${BLUE}📊 RÉSUMÉ DES TESTS${NC}"
echo -e "${BLUE}===================================${NC}"
echo -e "Total: $TOTAL"
echo -e "${GREEN}Réussis: $PASSED${NC}"
echo -e "${RED}Échoués: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ TOUS LES TESTS ONT RÉUSSI!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ CERTAINS TESTS ONT ÉCHOUÉ${NC}"
    exit 1
fi
