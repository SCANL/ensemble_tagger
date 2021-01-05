#ifndef WORDSFROMARCHIVEPOLICY
#define WORDSFROMARCHIVEPOLICY

#include <vector>
#include <ctype.h>
#include <exception>
#include <unordered_map>
#include <unordered_set>
#include <HTTPRequest.hpp>
#include <ClassPolicy.hpp>
#include <srcSAXHandler.hpp>
#include <DeclTypePolicy.hpp>
#include <ParamTypePolicy.hpp>
#include <srcSAXEventDispatcher.hpp>
#include <FunctionSignaturePolicy.hpp>
void hexchar(unsigned char c, unsigned char &hex1, unsigned char &hex2){
    hex1 = c / 16;
    hex2 = c % 16;
    hex1 += hex1 <= 9 ? '0' : 'a' - 10;
    hex2 += hex2 <= 9 ? '0' : 'a' - 10;
}

std::string urlencode(std::string s){
    const char *str = s.c_str();
    std::vector<char> v(s.size());
    v.clear();
    for (size_t i = 0, l = s.size(); i < l; i++){
        char c = str[i];
        if ((c >= '0' && c <= '9') ||
            (c >= 'a' && c <= 'z') ||
            (c >= 'A' && c <= 'Z') ||
            c == '-' || c == '_' || c == '.' || c == '!' || c == '~' ||
            c == '*' || c == '\'' || c == '(' || c == ')')
        {
            v.push_back(c);
        }
        else{
            v.push_back('%');
            unsigned char d1, d2;
            hexchar(c, d1, d2);
            v.push_back(d1);
            v.push_back(d2);
        }
    }

    return std::string(v.cbegin(), v.cend());
}
class WordsFromArchivePolicy : public srcSAXEventDispatch::EventListener, public srcSAXEventDispatch::PolicyDispatcher, public srcSAXEventDispatch::PolicyListener 
{
    private:
        std::string AnnotateIdentifier(std::string identifierType, std::string identifierName, std::string codeContext){
            try
            {
                // you can pass http::InternetProtocol::V6 to Request to make an IPv6 request
                std::string requestStr = "http://127.0.0.1:5000/"+urlencode(identifierType+"/"+identifierName+"/"+codeContext);
                std::cerr<<requestStr<<std::endl;
                http::Request request(requestStr);

                // send a get request
                const http::Response response = request.send("GET");
                return std::string(response.body.begin(), response.body.end());
            }
            catch (const std::exception& e)
            {
                std::cerr << "Request failed, error: " << e.what() << '\n';
                return "ERROR";
            }
            
        }
    public:
        ~WordsFromArchivePolicy(){};
        WordsFromArchivePolicy(std::initializer_list<srcSAXEventDispatch::PolicyListener*> listeners = {}) : srcSAXEventDispatch::PolicyDispatcher(listeners){
            // making SSP a listener for FSPP
            InitializeEventHandlers();
        
            declPolicy.AddListener(this);
            paramPolicy.AddListener(this);
            functionPolicy.AddListener(this);
        }
        void Notify(const PolicyDispatcher *policy, const srcSAXEventDispatch::srcSAXEventContext &ctx) override {}
        void NotifyWrite(const PolicyDispatcher *policy, srcSAXEventDispatch::srcSAXEventContext &ctx){
            using namespace srcSAXEventDispatch;
            if(typeid(DeclTypePolicy) == typeid(*policy)){
                decldata = *policy->Data<DeclData>();
                if(!(decldata.nameOfIdentifier.empty()||decldata.nameOfType.empty())){
                    if(ctx.IsOpen(ParserState::function)){
                        std::cerr<<"Raw Decl:"<<decldata.nameOfType<<" "<<decldata.nameOfIdentifier<<std::endl;
                        auto annotation = AnnotateIdentifier(decldata.nameOfType, decldata.nameOfIdentifier, "DECLARATION");
                        WriteElementToArchive(ctx, annotation);
                    }else if(ctx.IsOpen(ParserState::classn) && !decldata.nameOfContainingClass.empty() && !decldata.nameOfType.empty() && !decldata.nameOfIdentifier.empty()){
                        std::cerr<<"Raw Attr:"<<decldata.nameOfType<<" "<<decldata.nameOfIdentifier<<std::endl;
                        auto annotation = AnnotateIdentifier(decldata.nameOfType, decldata.nameOfIdentifier, "ATTRIBUTE");
                        WriteElementToArchive(ctx, annotation);
                    }
                }
            }else if(typeid(ParamTypePolicy) == typeid(*policy)){
                paramdata = *policy->Data<DeclData>();
                if(!(paramdata.nameOfIdentifier.empty() || paramdata.nameOfType.empty())){
                    std::cerr<<"Raw Param:"<<paramdata.nameOfType<<" "<<paramdata.nameOfIdentifier<<std::endl;
                    auto annotation = AnnotateIdentifier(paramdata.nameOfType, paramdata.nameOfIdentifier, "PARAMETER");
                    WriteElementToArchive(ctx, annotation);
                }
            }else if(typeid(FunctionSignaturePolicy) == typeid(*policy)){
                functiondata = *policy->Data<SignatureData>();
                std::string result;
                if(!(functiondata.name.empty() || functiondata.returnType.empty())){
                    if(functiondata.hasAliasedReturn) functiondata.returnType+="*";
                    std::cerr<<"Raw Func:"<<functiondata.returnType<<" "<<functiondata.name;
                    
                    result = "(";
                    for(auto param : functiondata.parameters){
                        result.append(param.nameOfType).append(" ").append(param.nameOfIdentifier).append(", ");
                    }
                    if(result.size()>1){
                        result.erase(result.size()-1);
                        result.erase(result.size()-1);
                    }
                    result.append(")");
                    std::cout<<result;
                }
                auto annotation = AnnotateIdentifier(functiondata.returnType, functiondata.name+result, "FUNCTION");
                WriteElementToArchive(ctx, annotation);
                //std::cout<<functiondata.name<<std::endl;
            }

        }
        void WriteElementToArchive(srcSAXEventDispatch::srcSAXEventContext &ctx, std::string posTag){
            //write the return type into srcML archive at the call site
            xmlTextWriterWriteElementNS(ctx.writer, (const xmlChar*)"src",(const xmlChar*) "grammar_pattern", (const xmlChar*)"http://www.srcML.org/srcML/src", BAD_CAST posTag.c_str());
        }
    
    protected:
        void *DataInner() const override {
            return (void*)0; // export profile to listeners
        }
        
    private:
        DeclTypePolicy declPolicy;
        DeclData decldata;

        ParamTypePolicy paramPolicy;
        DeclData paramdata;

        FunctionSignaturePolicy functionPolicy;
        SignatureData functiondata;

        std::string currentSLCategory;

        void InitializeEventHandlers(){
            using namespace srcSAXEventDispatch;
            openEventMap[ParserState::declstmt] = [this](srcSAXEventContext& ctx){
                ctx.dispatcher->AddListenerDispatch(&declPolicy);
            };
            openEventMap[ParserState::parameterlist] = [this](srcSAXEventContext& ctx) {
                ctx.dispatcher->AddListenerDispatch(&paramPolicy);
            };
            openEventMap[ParserState::function] = [this](srcSAXEventContext& ctx) {
                ctx.dispatcher->AddListenerDispatch(&functionPolicy);
            };
            closeEventMap[ParserState::classn] = [this](srcSAXEventContext& ctx){
                if(isupper(ctx.currentClassName[0])){ //heuristic-- class names that are not capitalized might be false positives
                    std::cerr<<"Raw Class:"<<ctx.currentClassName<<std::endl;
                    AnnotateIdentifier("class", ctx.currentClassName, "CLASS");

                }
            };
            closeEventMap[ParserState::functionblock] = [this](srcSAXEventContext& ctx){
                ctx.dispatcher->RemoveListenerDispatch(&functionPolicy);
            };
            closeEventMap[ParserState::declstmt] = [this](srcSAXEventContext& ctx){
                ctx.dispatcher->RemoveListenerDispatch(&declPolicy);
            };
            closeEventMap[ParserState::parameterlist] = [this](srcSAXEventContext& ctx) {
                ctx.dispatcher->RemoveListenerDispatch(&paramPolicy);
                //ctx.dispatcher->RemoveListenerDispatch(&functionPolicy);
            };
        }
};
#endif