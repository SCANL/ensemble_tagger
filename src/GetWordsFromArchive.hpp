#ifndef WORDSFROMARCHIVEPOLICY
#define WORDSFROMARCHIVEPOLICY

#include <ctype.h>
#include <exception>
#include <unordered_map>
#include <unordered_set>
#include <subprocess.hpp>
#include <ClassPolicy.hpp>
#include <srcSAXHandler.hpp>
#include <DeclTypePolicy.hpp>
#include <ParamTypePolicy.hpp>
#include <srcSAXEventDispatcher.hpp>
#include <FunctionSignaturePolicy.hpp>

using namespace subprocess;
class WordsFromArchivePolicy : public srcSAXEventDispatch::EventListener, public srcSAXEventDispatch::PolicyDispatcher, public srcSAXEventDispatch::PolicyListener 
{
    private:
        std::string AnnotateIdentifier(std::string identifierData, std::string codeContext){
            auto p = Popen({"python", "../ensemble_tagger_implementation/model_classification.py", identifierData, codeContext}, input{PIPE}, output{PIPE});
            std::cout << "Data in: " << identifierData << std::endl;
            auto obuf = p.communicate().first;
            std::cout << "Data out: " << obuf.buf.data() << std::endl;
            return obuf.buf.data();
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
        void Notify(const PolicyDispatcher *policy, const srcSAXEventDispatch::srcSAXEventContext &ctx) override {
            using namespace srcSAXEventDispatch;
            if(typeid(DeclTypePolicy) == typeid(*policy)){
                decldata = *policy->Data<DeclData>();
                if(!(decldata.nameOfIdentifier.empty()||decldata.nameOfType.empty())){
                    if(ctx.IsOpen(ParserState::function)){
                        std::cout<<"Raw Decl:"<<decldata.nameOfType<<" "<<decldata.nameOfIdentifier<<std::endl;
                        AnnotateIdentifier(decldata.nameOfType + ' ' + decldata.nameOfIdentifier, "DECLARATION");
                    }else if(ctx.IsOpen(ParserState::classn) && !decldata.nameOfContainingClass.empty() && !decldata.nameOfType.empty() && !decldata.nameOfIdentifier.empty()){
                        std::cout<<"Raw Attr:"<<decldata.nameOfType<<" "<<decldata.nameOfIdentifier<<std::endl;
                        AnnotateIdentifier(decldata.nameOfType + ' ' + decldata.nameOfIdentifier, "ATTRIBUTE");
                    }
                }
            }else if(typeid(ParamTypePolicy) == typeid(*policy)){
                paramdata = *policy->Data<DeclData>();
                if(!(paramdata.nameOfIdentifier.empty() || paramdata.nameOfType.empty())){
                    std::cout<<"Raw Param:"<<paramdata.nameOfType<<" "<<paramdata.nameOfIdentifier<<std::endl;
                    AnnotateIdentifier(paramdata.nameOfType + ' ' + paramdata.nameOfIdentifier, "PARAMETER");
                }
            }else if(typeid(FunctionSignaturePolicy) == typeid(*policy)){
                functiondata = *policy->Data<SignatureData>();
                if(!(functiondata.name.empty() || functiondata.returnType.empty())){
                    std::cout<<"Raw Func:"<<functiondata.returnType<<" "<<functiondata.name<<std::endl;
                }
                //std::cout<<functiondata.name<<std::endl;
            }
            
        }
        void NotifyWrite(const PolicyDispatcher *policy, srcSAXEventDispatch::srcSAXEventContext &ctx){}
    
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
                    std::cout<<"Raw Class:"<<ctx.currentClassName<<std::endl;
                    AnnotateIdentifier("class "+ ctx.currentClassName, "CLASS");

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